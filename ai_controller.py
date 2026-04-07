import google.generativeai as genai

class AIController:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = None
        
        try:
            # Mavjud barcha modellarni ko'rib chiqamiz
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Eng yaxshisi 'gemini-1.5-flash', agar u bo'lsa uni olamiz
                    if 'gemini-1.5-flash' in m.name:
                        self.model = genai.GenerativeModel(m.name)
                        break
            
            # Agar flash topilmasa, ro'yxatdagi birinchi ishlaydigan modelni olamiz
            if not self.model:
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                if models:
                    self.model = genai.GenerativeModel(models[0])
                    
        except Exception as e:
            print(f"Modellarni aniqlashda xato: {e}")

    def tahlil_va_maslahat(self, kod, xato):
        if not self.model:
            return "Xatolik: Tizimda ishlaydigan AI modeli topilmadi."

        prompt = f"""Siz magistrlik loyihasidagi repetitorsiz. 
        Talaba kodi: {kod}
        Xatolik: {xato}
        Vazifa: Talabaga xatosini topishga yordam beruvchi savol bering. 
        Javobingiz faqat O'zbek tilida bo'lsin."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI javob bera olmadi: {str(e)}"