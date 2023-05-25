import fitz, os, logging, re, pdfplumber

from modules.document_modules.file_reading.file_reading_abstract import FileReadingAbstract

class PDFReader(FileReadingAbstract):
    __instance = None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            
        return cls.__instance
    
    def get_text(cls, filepath, keyword="", split_by='H2', split='headers'):
        """Grabs the text from a pdf and returns it as a list of strings.
        This is the case even if the pdf is a single page or the setting is not set to split at all (i.e. split_by='').
        Returning a list of strings allows for easier processing of the text as output will be consistent.

        Args:
            filepath (str): location of document.
            keyword (str, optional): _description_. Defaults to "".
            split_by (str, optional): _description_. Defaults to 'H2'.
            split (str, optional): _description_. Defaults to 'headers'.

        Returns:
            _type_: _description_
        """
        split = split.lower().strip()
        if split in ['headers', 'header', 'h']:
            try:
                return cls.__split_by_headers(filepath, keyword, split_by)
            except KeyError:
                logging.warning("Unable to identify headers. Defaulting to page split.")
                return cls.__split_by_page(filepath)
        elif split in ['page', 'pages']:
            return cls.__split_by_page(filepath)
        else:
            return cls.__get_whole_doc(filepath)
        
    @staticmethod
    def __split_by_page(filepath): 
        with pdfplumber.open(filepath) as pdf:
            pages = []
            for i in range(len(pdf.pages)):
                pages.append(pdf.pages[i].extract_text())
                
        return pages
    
    @staticmethod
    def __get_whole_doc(filepath): 
        with pdfplumber.open(filepath) as pdf:
            pages = []
            for i in range(len(pdf.pages)):
                pages.append(pdf.pages[i].extract_text())
                
        return [" ".join(pages)]

    @classmethod
    def __split_by_headers(cls, filepath, keyword="", split_by='H2'): 
        headers_obj, full_extraction = cls.__get_headers(filepath, keyword)
        text = cls.__split_into_text(headers_obj, full_extraction, split_by)
        
        nl = []
        for i in range(len(text)):
            if len(text[i].strip()) < 3:
                continue
            text[i] = text[i].replace(u'\xa0', u' ')
            nl.append(text[i])
                
        
        
        return nl
    
    @classmethod
    def __get_headers(cls, filepath, keyword=""):
        full_extraction = cls.__get_font_info(filepath, keyword)
        scores, average_font_size = cls.__get_list_of_font_sizes(filepath, keyword)
        # pprint(scores)
        arr_of_valid_header_sizes = cls.__filter_font_sizes(full_extraction, scores, average_font_size) # complete
        arr_of_valid_header_sizes = sorted(arr_of_valid_header_sizes, key=float)
        
        headers_obj = {}
        
        counter = 1
        for i in reversed(arr_of_valid_header_sizes):
            headers_obj['h' + str(counter)] = i
            counter += 1
            
        
        return headers_obj, full_extraction
    
    @staticmethod
    def __get_font_info(filePath, keyword=""):
        results = [] # list of tuples that store the information as (text, font size, font name) 
        pdf = fitz.open(filePath) # filePath is a string that contains the path to the pdf
        for page in pdf:
            text_dict = page.get_text("dict")
            blocks = text_dict["blocks"]
            for block in blocks:
                if "lines" in block.keys():
                    spans = block['lines']
                    for span in spans:
                        data = span['spans']
                        for lines in data:
                            if keyword == "":
                                if keyword in lines['text'].lower(): # only store font information of a specific keyword
                                    results.append((lines['text'], lines['size'], lines['font']))
                                    # lines['text'] -> string, lines['size'] -> font size, lines['font'] -> font name
                            else:
                                 results.append((lines['text'], lines['size'], lines['font']))
        pdf.close()
        return results
         
    @classmethod
    def __get_list_of_font_sizes(cls, filepath, keyword=""):
        original_list = cls.__get_font_info(filepath, keyword)
        flat_list = [item for sublist in original_list for item in sublist]
        total = 0
        
        for item in flat_list:
            if type(item) == float:
                total += 1
        
        lst = [x[1] for x in original_list]
        lst = list(set(lst))
        scores = {}
        
        for size in lst:
            count = flat_list.count(size)
            if count > 1:
                scores[cls.__round(size)] = count
                
        return scores, max(scores, key=scores.get)
    
    @classmethod
    def __filter_font_sizes(cls, fill_extraction, scores, average_font_size):
        
        header_sizes = []
        
        # grab all fonts larger than standard font size
        for p in scores.keys():
            if p > average_font_size:
                header_sizes.append(p)
        
        for size in header_sizes:
            arr = cls.__get_list_with_this_font(fill_extraction, size)
            if all([item[0].isdigit() for item in arr]) == True:
                header_sizes.remove(size)
        
        return header_sizes
    
    @staticmethod
    def __round(x):
        return float(round(x))
    
    @classmethod
    def __get_list_with_this_font(cls, full_extraction, font_size):
        arr = []
        for line in full_extraction:
            if cls.__round(line[1]) == font_size:
                arr.append(line)
                
        return arr
    
    @staticmethod
    def __split_into_text(headers_obj, full_extraction, split_by) -> list:
        split_by = split_by.lower()
        split_size = 0.0
        if split_by == 'h1':
            split_size = headers_obj['h1']
        elif split_by == 'h2':
            try:
                split_size = headers_obj['h2']
            except KeyError:
                split_size = headers_obj['h1']
        elif split_by == 'h3':
            try:
                split_size = headers_obj['h3']
            except KeyError:
                try:
                    split_size = headers_obj['h2']
                except KeyError:
                    split_size = headers_obj['h1']
        elif split_by == 'h4':
            try:
                split_size = headers_obj['h4']
            except KeyError:
                try:
                    split_size = headers_obj['h3']
                except KeyError:
                    try:
                        split_size = headers_obj['h2']
                    except KeyError:
                        split_size = headers_obj['h1']
        else:
            try:
                try:
                    if split_by.lower() in headers_obj.keys():
                        split_size = headers_obj[split_by.lower()]
                except Exception:
                    split_size = headers_obj['h2']
                    logging.warning("Invalid value selected. Defaulting to H2.")
            except KeyError:
                split_size = headers_obj['h1']
                logging.warning("Invalid value selected. Defaulting to H1.")
            
        arr = {') ', '] ', '. '}
        text = []
        string = ""
        
        for line in full_extraction:
            if PDFReader.__round(line[1]) == split_size and string != "":
                text.append(string)
                string = ""
                
                ## detect font type <<<< write this next and label them with like [italics] or something
                
            string += line[0]
            if line[0][0] not in arr:
                string += " "
        return text

    
    