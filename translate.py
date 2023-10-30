import requests

class LibreTranslate:
    BASE_URL = "https://libretranslate.de/translate"

    def translate_text(self, text, source_language, target_language):
        payload = {
            "q": text,
            "source": source_language,
            "target": target_language
        }

        response = requests.post(self.BASE_URL, data=payload)

        if response.status_code != 200:
            return f"Error: {response.status_code}"

        translated_text = response.json()['translatedText']
        return translated_text

if __name__ == "__main__":
    translator = LibreTranslate()
    text_to_translate = " 안녕하세요, 당신은?"
    source_language = "ko"
    target_language = "en"  #to english

    translated = translator.translate_text(text_to_translate, source_language, target_language)
    print(f"Original: {text_to_translate}")
    print(f"Translated: {translated}")
