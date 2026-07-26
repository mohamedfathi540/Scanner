import os 
import importlib
from Stores.LLM.Templates.Locales.en.production_extraction import FOAM_EXTRACTION_PROMPT
from Stores.LLM.Templates.Locales.en.section_registry import get_section

class template_parser : 
    def __init__(self , language : str = None ,default_language : str = "en") : 
        self.current_path  = os.path.dirname (os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None

        self.set_language(language)

    def get_production_prompt(self, section: str = "foam") -> str:
        """
        Return the OCR extraction prompt for a given production section.
        Falls back to the Foam prompt if section is unrecognized or not yet configured.
        """
        cfg = get_section(section)
        if cfg and cfg.get("prompt_module") and cfg.get("prompt_var"):
            try:
                mod = importlib.import_module(cfg["prompt_module"])
                return getattr(mod, cfg["prompt_var"])
            except (ImportError, AttributeError):
                pass
        # Fallback to Foam prompt
        return FOAM_EXTRACTION_PROMPT


    def set_language(self , language : str) : 

        if not language : 
            self.language = self.default_language
        
        language_path = os.path.join(self.current_path,"Locales", language)
        if os.path.exists(language_path) :
            self.language = language
        else :
            self.language = self.default_language



    def get(self,group :str ,key : str , vars : dict = {} ):
        if not group or not key : 
            return None
        
        group_path = os.path.join(self.current_path,"Locales", self.language, f"{group}.py")
        targeted_language = self.language
        if not os.path.exists(group_path) :
            group_path = os.path.join(self.current_path,"Locales", self.default_language, f"{group}.py")
            targeted_language = self.default_language
        
        if not os.path.exists(group_path) :
            return None
        

        # import module 
        module = __import__(f"Stores.LLM.Templates.Locales.{targeted_language}.{group}",fromlist=[group] ) 


        if not module :
            return None
        

        key_attribute = getattr(module,key)
        return key_attribute.substitute(vars)
