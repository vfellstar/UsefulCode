from datetime import datetime
import os, shutil


class Document():
    def __init__(self, id, file_location):
        self.__id = id
        self.__file_location = file_location
        self.__logged_time = datetime.now().isoformat()
        self.__categorisation_details = {}
        self.__extraction_details  = {}
        self.__enhancement_details = {}
    
    @property
    def upload_time(self):
        return self.__logged_time
    
    @property
    def id(self):
        return self.__id
    
    @property
    def file_location(self):
        return self.__file_location
    
    def change_file_location(self, new_location):
        try: 
            if os.path.exists(self.__file_location):
                shutil.move(self.__file_location, new_location)
                self.__file_location = new_location
        except Exception as e:
            print(e)
            
    # docker tag neo-classifier-server_worker registry.unigw.dev/neo-classifier-server_worker:latest 
    # docker push registry.unigw.dev/neo-classifier-server_worker:latest