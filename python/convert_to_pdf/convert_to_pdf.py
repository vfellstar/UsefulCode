import os, sys, subprocess, re, textwrap
from fpdf import FPDF
from PIL import Image
import multiprocessing as mp

from typing import Union
from etc.env_settings import Setting
from modules.redis_connection import RedisConnection


class ConvertToPDF:
    
    __lock = None
    __instance = None
    __converted_dir = Setting.CONVERTED_DIR.value
    
    class LibreOfficeError(Exception):
        def __init__(self, output):
            self.output = output
            print(str(output).upper())
            
    @staticmethod
    def libreoffice_exec():
        if sys.platform == 'darwin':
            return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
        return 'libreoffice'
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__lock = mp.Lock()
            
        return cls.__instance
    
    @classmethod
    def view_file(cls, filepath):
        if filepath.endswith(".pdf"):
            return filepath
        
        # check if already converted
        is_converted_already = cls.__is_converted(filepath)
        if type(is_converted_already) == str:
            return is_converted_already
        
        # convert
        pdf_file = cls.__convert_to_pdf(filepath)
        return pdf_file
    
    @classmethod
    def __convert_to_pdf(cls, filepath:str):
        if filepath.endswith(".docx"):
            return cls.__docx_to_pdf(filepath)
        elif filepath.endswith(".txt"):
            return cls.__txt_to_pdf(filepath)
        elif filepath.endswith(".png") or filepath.endswith(".jpg") or filepath.endswith(".jpeg"):
            return cls.__images_to_pdf(filepath)
        else:
            raise ValueError("File type not supported.")
    
    @classmethod
    def __docx_to_pdf(cls, filepath:str):
        """Converts the given file into a pdf file.

        Args:
            url (str): location of the file.
            
        Returns:
            str: location of the pdf file.
        """
        with cls.__lock:
            args = [cls.libreoffice_exec(), '--headless', '--convert-to', 'pdf', '--outdir', cls.__converted_dir, filepath]
            process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=None)
            filename = re.search('-> (.*?) using filter', process.stdout.decode())
        
            if filename is None:
                raise cls.LibreOfficeError(process.stdout.decode())
            else:
                return filename.group(1)
            
    @classmethod
    def __is_converted(cls, filepath:str) -> Union[str, bool]:
        filename = os.path.basename(filepath)
        basename = os.path.splitext(filename)[0]
        pdf_file = os.path.join(cls.__converted_dir, basename + ".pdf")
        if os.path.isfile(pdf_file):
            return pdf_file
        return False
    
    @classmethod
    def __images_to_pdf(cls, filepath:str):
        filename = os.path.basename(filepath)
        basename = os.path.splitext(filename)[0]
        output = os.path.join(cls.__converted_dir, basename + ".pdf")
        img = Image.open(filepath)
        img = img.convert('RGB')
        img.save(output)
        return output
        
    @classmethod
    def __txt_to_pdf(cls, filepath:str):
        filename = os.path.basename(filepath)
        basename = os.path.splitext(filename)[0]
        output = os.path.join(cls.__converted_dir, basename + ".pdf")
        
        with open(filepath, "r") as f:
            text = f.read()
            
        a4_width_mm = 210
        pt_to_mm = 0.35
        fontsize_pt = 10
        fontsize_mm = fontsize_pt * pt_to_mm
        margin_bottom_mm = 10
        character_width_mm = 7 * pt_to_mm
        width_text = a4_width_mm / character_width_mm

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(True, margin=margin_bottom_mm)
        pdf.add_page()
        pdf.set_font(family='Courier', size=fontsize_pt)
        splitted = text.split('\n')

        for line in splitted:
            lines = textwrap.wrap(line, width_text)

            if len(lines) == 0:
                pdf.ln()

            for wrap in lines:
                pdf.cell(0, fontsize_mm, wrap, ln=1)

        
        pdf.output(output, 'F').encode('latin-1')
        return output
        