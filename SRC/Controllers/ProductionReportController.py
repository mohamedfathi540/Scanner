# SRC/Controllers/ProductionReportController.py

import pandas as pd
import json
import os
import re
import tempfile
import logging
from io import BytesIO
from datetime import datetime
from fastapi import UploadFile
from Models.DB_Schemes.minirag.Schemes.Project import Project
from sqlalchemy.orm import Session
from Stores.OCR.OCRProviderFactory import OCRProviderFactory
from Stores.LLM.Templates.template_parser import template_parser as TemplateParser
from Stores.LLM.Templates.Locales.en.section_registry import get_section
from Helpers.Config import get_settings

logger = logging.getLogger("uvicorn.error")


def enhance_image_for_ocr(image_bytes: bytes) -> bytes:
    """
    Lightweight OpenCV pre-processing to darken grid lines and boost
    ink contrast before sending the image to the Vision AI.

    This is critical for handwritten Arabic manufacturing logs where
    faint printed grid lines cause the AI to lose track of columns.
    """
    if not image_bytes or len(image_bytes) < 100:
        logger.warning("Image bytes too small (%d bytes) — skipping enhancement", len(image_bytes) if image_bytes else 0)
        return image_bytes

    try:
        import cv2
        import numpy as np

        # Decode image bytes into a grayscale OpenCV matrix
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if img is None:
            logger.warning("OpenCV could not decode image — skipping enhancement")
            return image_bytes

        # --- Stage 1: Aggressive contrast boost to make grid lines pop ---
        # alpha > 1 increases contrast, beta < 0 darkens the midtones
        alpha = 1.5   # Contrast multiplier
        beta = -50    # Brightness offset (negative = darker)
        enhanced = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

        # --- Stage 2: Adaptive threshold sharpening (optional extra clarity) ---
        # CLAHE (Contrast Limited Adaptive Histogram Equalization) enhances
        # local contrast without blowing out already-dark regions
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(enhanced)

        # Re-encode to JPEG bytes for the AI
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]
        _, buffer = cv2.imencode('.jpg', enhanced, encode_params)

        logger.info(
            "Image enhanced for OCR: %d bytes → %d bytes",
            len(image_bytes), len(buffer)
        )
        return buffer.tobytes()
    except Exception as e:
        logger.warning("Image enhancement failed (%s) — using original image", e)
        return image_bytes


class ProductionReportController:
    def __init__(self):
        # We use the factory pattern from RxTract
        settings = get_settings()
        self.ocr_provider = OCRProviderFactory(settings).create("GEMINI")
        self.template_parser = TemplateParser(language='en')

    def force_clean_numbers(self, row, numeric_fields: list[str]):
        """Forces columns to be strictly numbers, ignoring any leaked text."""
        for field in numeric_fields:
            if field not in row:
                row[field] = 0
                continue

            val = str(row.get(field, "0"))
            
            # If the AI accidentally put "MAX 5" into a number field, extract "MAX" to brand
            if "Brand_Repair" in row:
                if "MAX" in val.upper():
                    row["Brand_Repair"] = "MAX"
                elif "HT" in val.upper():
                    row["Brand_Repair"] = "HT"
                
            # Translate Arabic/Persian numerals to standard English digits
            val = val.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789'))
            
            # Regex: Remove EVERYTHING except digits (0-9)
            clean_digits = re.sub(r'[^\d]', '', val)
            
            # Convert to integer, default to 0 if blank
            row[field] = int(clean_digits) if clean_digits else 0

        # Mathematical Validation (only for sections that have these columns)
        if all(k in row for k in ("Total_Qty", "Inspect_Sound_Qty", "Inspect_Scrap_Qty", "Repair_Qty")):
            total = row["Total_Qty"]
            calculated_sum = row["Inspect_Sound_Qty"] + row["Inspect_Scrap_Qty"] + row["Repair_Qty"]

            if total > 0 and total != calculated_sum:
                # Fix 50 vs 51 read errors
                if total == (calculated_sum + 1) or total == (calculated_sum - 1):
                    row["Total_Qty"] = calculated_sum 
                
        return row

    @staticmethod
    def _extract_json_from_response(raw_response: str) -> str:
        """
        Strip the <scratchpad> block and any markdown fences from the AI
        response, then extract the JSON array.

        The AI now outputs:
            <scratchpad>...thinking...</scratchpad>
            ```json
            [ { ... }, { ... } ]
            ```
        We need to isolate just the JSON array.
        """
        text = raw_response.strip()

        # 1. Remove the entire <scratchpad>...</scratchpad> block
        text = re.sub(
            r'<scratchpad>.*?</scratchpad>',
            '',
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        # 2. Remove markdown code fences
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()

        # 3. Find the JSON array — grab everything from first '[' to last ']'
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]

        return text

    async def process_report_to_excel(self, file: UploadFile, db: Session, section: str = "foam"):
        # Validate section
        section_cfg = get_section(section)
        if not section_cfg:
            raise ValueError(f"Unknown section: '{section}'")
        if not section_cfg.get("prompt_module"):
            raise ValueError(f"Section '{section_cfg['name']}' is not configured yet. Please set up its OCR prompt first.")

        image_bytes = await file.read()
        
        # ── Pre-processing: boost contrast to make grid lines visible to AI ──
        enhanced_bytes = enhance_image_for_ocr(image_bytes)

        # Save enhanced image to temp file for OCR provider compatibility
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
            temp_img.write(enhanced_bytes)
            temp_path = temp_img.name

        try:
            # 1. Call the AI with the enhanced image and the section-specific prompt
            prompt = self.template_parser.get_production_prompt(section)
            json_response = self.ocr_provider.ocr_image(
                temp_path,
                prompt,
                max_output_tokens=16384,  # Extra room for scratchpad + JSON
            )
        finally:
            os.remove(temp_path)
            
        if not json_response:
            raise ValueError("The AI returned an empty response.")
        
        # 2. Parse the response: strip scratchpad, extract JSON
        clean_json = self._extract_json_from_response(json_response)
        
        try:
            data = json.loads(clean_json)
        except json.JSONDecodeError:
            logger.error(
                "Failed to parse JSON from AI response. Raw (first 1000 chars): %s",
                json_response[:1000]
            )
            raise ValueError("Failed to parse response into valid JSON structure.")
            
        # 3. Python Regex Cleaning & Math Integrity Check
        numeric_cols = section_cfg["numeric_columns"]
        validated_data = [self.force_clean_numbers(row, numeric_cols) for row in data]
        
        # 4. Create DataFrame and enforce column order from section config
        df = pd.DataFrame(validated_data)
        columns_order = section_cfg["columns"]
        
        # Add any missing columns as empty to prevent Pandas from failing
        for col in columns_order:
            if col not in df.columns:
                df[col] = ""
                
        df = df[columns_order]  # Reorder to match section specification

        # 5. Export to Excel in memory (no file saved to disk)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_prefix = section_cfg["file_prefix"]
        filename = f"{file_prefix}_{timestamp}.xlsx"

        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        
        # 6. Database Logging
        new_log = Project(
            filename=file.filename,
            rows_extracted=len(df),
            status="SUCCESS"
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        
        return buffer, filename
