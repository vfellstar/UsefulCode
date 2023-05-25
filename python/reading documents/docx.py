import docx, os

class DocxReader():
    
    def get_text(self, full_path:str) -> list: # multiple processes can call this
        doc = docx.Document(full_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text) if para.text != "" else None
            
        return full_text


    
    