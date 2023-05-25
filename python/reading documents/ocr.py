import pytesseract
from PIL import Image
from autocorrect import Speller

__spell = Speller(only_replacements=True)
def read_image( url):
    content:str = pytesseract.image_to_string(Image.open(url))
    if not content.strip():
        return "[Empty]"
    else:
        content = content.strip()
    content = __spell(content)
    return content