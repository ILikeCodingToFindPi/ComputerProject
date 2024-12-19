import requests

def ocr_space_file(filename, overlay=True, api_key='K82693734788957', language='eng'):
    """ OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available langauage codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               'OCREngine':2
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          
                          )
    return r.content.decode()
# Extract plain text from the OCR JSON response
def extract_plain_text(json_response):
    """Extract plain text from the OCR JSON response."""
    try:
        data = json.loads(json_response)
        parsed_results = data.get('ParsedResults', [])
        
        if not parsed_results:
            return "No text found in the image."
        
        plain_text = ""
        for result in parsed_results:
            plain_text += result.get('ParsedText', '') + '\n'
        return plain_text.strip()
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


filename = '/content/example.png'  


test_file = ocr_space_file(filename=filename, language='eng')


plain_text = extract_plain_text(test_file)
print(plain_text)

