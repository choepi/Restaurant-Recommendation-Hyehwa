import requests

def translate_korean_to_english(korean_text):
    url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
    
    payload = {
        "q": korean_text,
        "target": "en",
        "source": "ko"
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "application/gzip",
        "X-RapidAPI-Key": "2f168c8413msh98205027eeeb4d9p1410bejsn6f4d9cf9b76e",
        "X-RapidAPI-Host": "google-translate1.p.rapidapi.com"
    }

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result['data']['translations'][0]['translatedText']
    else:
        return "Error: Unable to translate"

# Example usage:
text = "즐겨찾기로 편리하게 찾아 보실 수 있습니다."
translated_text = translate_korean_to_english(text)
print(translated_text)
