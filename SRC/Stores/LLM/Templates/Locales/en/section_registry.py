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
        "name_ar": "قسم التجميع والتغليف",
        "file_prefix": "HT_Sewing_Report",
        "prompt_module": "Stores.LLM.Templates.Locales.en.sewing_extraction",
        "prompt_var": "SEWING_EXTRACTION_PROMPT",
        "columns": [
            "Item_Name",
            "Order_No",
            "Delivered_Sound_Qty",
            "Delivered_Scrap_Qty",
            "Samples_10_Percent",
            "Accepted_Samples",
            "Rejected_Samples",
            "Addition",
            "Resort_Decision",
            "Production_Qty",
            "Samples_30_Percent",
            "Notes",
            "Final_Sound_Qty",
            "Final_Scrap_Qty"
        ],
        "numeric_columns": [
            "Delivered_Sound_Qty", "Delivered_Scrap_Qty", "Samples_10_Percent",
            "Accepted_Samples", "Rejected_Samples", "Addition", "Production_Qty",
            "Samples_30_Percent", "Final_Sound_Qty", "Final_Scrap_Qty"
        ],
    },
    "packing": {
        "name": "Packing",
        "name_ar": "التعبئة",
        "file_prefix": "HT_Packing_Report",
        "prompt_module": "Stores.LLM.Templates.Locales.en.packing_extraction",
        "prompt_var": "PACKING_EXTRACTION_PROMPT",
        "columns": [
            "Item_Name",
            "Order_No",
            "Prod_Sound_Qty",
            "Rework_Qty",
            "Delivered_To_Quality_Qty",
            "Samples_Count",
            "Accepted_Samples_Count",
            "Rejected_Samples_Count",
            "Production_Decision",
            "Sorting_Prod_Qty",
            "Sorting_Samples_Count",
            "Notes",
            "Quality_Sound_Qty",
            "Quality_Scrap_Qty"
        ],
        "numeric_columns": [
            "Prod_Sound_Qty", "Rework_Qty", "Delivered_To_Quality_Qty",
            "Samples_Count", "Accepted_Samples_Count", "Rejected_Samples_Count",
            "Sorting_Prod_Qty", "Sorting_Samples_Count", "Quality_Sound_Qty",
            "Quality_Scrap_Qty"
        ],
    },
    "shoes": {
        "name": "Shoes",
        "name_ar": "الأحذية",
        "file_prefix": "HT_Shoes_Report",
        "prompt_module": "Stores.LLM.Templates.Locales.en.shoes_extraction",
        "prompt_var": "SHOES_EXTRACTION_PROMPT",
        "columns": [
            "Item_Name",
            "Order_No",
            "Prod_Sound_Qty",
            "Prod_Scrap_Qty",
            "Total_Qty",
            "Inspect_Sound_Qty",
            "Inspect_Scrap_Qty",
            "Repair_Qty",
            "Repair_Reason",
            "Notes",
            "Final_Sound_Qty",
            "Final_Scrap_Qty"
        ],
        "numeric_columns": [
            "Prod_Sound_Qty", "Prod_Scrap_Qty", "Total_Qty",
            "Inspect_Sound_Qty", "Inspect_Scrap_Qty", "Repair_Qty", 
            "Final_Sound_Qty", "Final_Scrap_Qty"
        ],
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
