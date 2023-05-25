import re
from bs4 import BeautifulSoup
from typing import Union

from modules.document_modules.file_reading.file_reading_abstract import FileReadingAbstract


class HTMLReader(FileReadingAbstract):
    
    def get_text(self, filepath:str):
        with open(filepath, "r") as f:
            text = f.read()
            return self.read_html(text)
    
    def read_html(self, html_str):
        soup = BeautifulSoup(html_str, "html.parser")
        tag = soup.body  
        strings = ""
        for string in tag.strings:
            strings = strings + " " + string
        strings = self.__remove_from_html(strings)
        return [strings.strip()]
    
    def get_shortdesc(self, filepath) -> Union[bool, list]:
        if '.html' not in str(filepath):
            return False
        
        try:
            with open(filepath, 'r') as f:
                text = f.read()
                if '<shortdesc ' in text:
                    soup = BeautifulSoup(text, 'html.parser')
                    return soup.shortdesc.text
        except UnicodeDecodeError:
            print(filepath)
                
                
        return False
    
    def __remove_from_html(self, string):
        to_remove = ['This site works best with JavaScript enabled',
                     'See also\nUser help home page',
                     'See also\nAdmin help home page']
        
        new_string = string
        
        for i in to_remove:
            if i in new_string:
                new_string = new_string.replace(i, "")
                
        new_string = new_string.replace('\xa0', ' ')
        
        remove_items = ["  ", "\n", "\t", "\r"]
        for item in remove_items:
            while item in new_string:
                new_string = new_string.replace(item, " ")
        
                
        return new_string
    