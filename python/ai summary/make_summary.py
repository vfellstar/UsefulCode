import re, nltk, heapq
from transformers import pipeline

class CreateShortDesc:
    
    def __init__(self) -> None:
        """Create instance of 'CreateShortDesc' class
        """
        pass
    
    def __preprocessing(self, text):
        text = re.sub(r'\[[0-9]*\]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        formatted_article_text = re.sub('[^a-zA-Z]', ' ', text)
        formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)
        return text , formatted_article_text
    
    def __create_short_desc(self, text):
        stopwords = nltk.corpus.stopwords.words('english')
        text, formatted_article_text = self.__preprocessing(text)
        sentence_list = nltk.sent_tokenize(text)
        word_frequencies = {}
        for word in nltk.word_tokenize(formatted_article_text):
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
                    
        maximum_frequncy = max(word_frequencies.values())

        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
            
        sentence_scores = {}
        for sent in sentence_list:
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]
                            
        summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)

        summary = ' '.join(summary_sentences)
            
        return summary

    def create_short_desc(self, text, percentage=None):
        
        if percentage == None:
            full_len = len(text)
            summary = self.__create_short_desc(text)
            if len(summary) > (full_len * 0.3):
                summary = self.__create_short_desc(text)
            return summary
        else: 
            full_len = len(text)
            summary = self.__create_short_desc(text)
            if len(summary) > (full_len * percentage):
                summary = self.__create_short_desc(text)
            return summary
            



class MLShortDescCreator:

    def __init__(self):
        self.__summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.__max_length = 1000
        self.__shorten = CreateShortDesc()
    
    def create_short_desc(self, ARTICLE):
        success = False
        
        while len(ARTICLE.split(" ")) > 650:
            ARTICLE = self.__shorten.create_short_desc(ARTICLE, 0.9)
        
        while not success:
            try:
                res = self.__summarizer(ARTICLE, min_length=30, do_sample=False)
                success = True
                summary = res[0]['summary_text']
                
                if len(ARTICLE) < len(summary):
                    return "N/A"
                return summary + "\n[AI Generated Summary]"
            
            except Exception:
                self.__max_length -= 100
                
    