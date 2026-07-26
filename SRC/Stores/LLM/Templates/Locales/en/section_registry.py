# SRC/Stores/LLM/Templates/Locales/en/section_registry.py

"""
Central registry of all production sections.

To add a new section:
1. Create a prompt file (e.g., sewing_extraction.py) with SEWING_EXTRACTION_PROMPT
2. Add the section entry to SECTIONS dict below
3. The backend route and frontend will pick it up automatically
"""

SECTIONS = {
    "foam": {
        "name": "Foam",
        "name_ar": "الفوم",
        "file_prefix": "HT_Foam_Report",
        "prompt_module": "Stores.LLM.Templates.Locales.en.production_extraction",
        "prompt_var": "FOAM_EXTRACTION_PROMPT",
        "columns": [
            "Item_Name", "Order_No", "Prod_Sound_Qty", "Prod_Scrap_Qty",
            "Total_Qty", "Inspect_Sound_Qty", "Inspect_Scrap_Qty", "Repair_Qty",
            "Repair_Reason", "Notes_Defects", "Final_Sound_Qty", "Final_Scrap_Qty",
            "Brand_Repair",
        ],
        "numeric_columns": [
            "Prod_Sound_Qty", "Prod_Scrap_Qty", "Total_Qty",
            "Inspect_Sound_Qty", "Inspect_Scrap_Qty", "Repair_Qty",
            "Final_Sound_Qty", "Final_Scrap_Qty",
        ],
    },
    "sewing": {
        "name": "Sewing",
        "name_ar": "الخياطة",
        "file_prefix": "HT_Sewing_Report",
        "prompt_module": None,  # TODO: create sewing_extraction.py
        "prompt_var": None,
        "columns": [],          # TODO: define sewing columns
        "numeric_columns": [],
    },
    "packing": {
        "name": "Packing",
        "name_ar": "التعبئة",
        "file_prefix": "HT_Packing_Report",
        "prompt_module": None,  # TODO: create packing_extraction.py
        "prompt_var": None,
        "columns": [],          # TODO: define packing columns
        "numeric_columns": [],
    },
    "shoes": {
        "name": "Shoes",
        "name_ar": "الأحذية",
        "file_prefix": "HT_Shoes_Report",
        "prompt_module": None,  # TODO: create shoes_extraction.py
        "prompt_var": None,
        "columns": [],          # TODO: define shoes columns
        "numeric_columns": [],
    },
}


def get_section(section_key: str) -> dict | None:
    """Return section config or None if not found."""
    return SECTIONS.get(section_key)


def get_available_sections() -> list[dict]:
    """Return list of all sections with their metadata and readiness status."""
    result = []
    for key, cfg in SECTIONS.items():
        result.append({
            "key": key,
            "name": cfg["name"],
            "name_ar": cfg["name_ar"],
            "ready": cfg["prompt_module"] is not None,
        })
    return result
