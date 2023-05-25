import urllib.request

from modules.document_modules.file_reading.file_reading_abstract import FileReadingAbstract
from modules.document_modules.file_reading.html import HTMLReader


class WebpageReader(FileReadingAbstract):
    
    def __init__(self) -> None:
        self.__html_reader = HTMLReader()
    
    def get_text(self, url:str):
        with urllib.request.urlopen(url) as fp:
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            
            
        return self.__html_reader.read_html(mystr)
        
        
    
    