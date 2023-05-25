import moviepy.editor
import os
import pickle
import time
from datetime import datetime, timedelta

from etc.settings import Settings
from code.redis_connection import RedisConnection
from code.settings_manager import SettingsManager

class WavGetter():
    
    def __init__(self):
        self.__settings_manager = SettingsManager()
        self.__extracted_audio_folder = Settings.extracted_audio_dir.value 
        self.__extracted_audio_lifetime = {}
        self.__redis = RedisConnection().redis
        
        wav_lifetime = self.__settings_manager.get_setting("wav_lifetime")
        self.__wav_lifetime = wav_lifetime if wav_lifetime > 3600 else 3600
        
        if self.__redis.exists("extracted_audio_lifetime") == 0:
            self.__redis.set("extracted_audio_lifetime", pickle.dumps(self.__extracted_audio_lifetime))
            
    def _synchronise_data(foo):
        """Decorator to call before methods that use extracted_audio_tracker.

        Args:
            foo (_type_): _description_
        """
        def fooer(self, *args, **kwargs):
            self.__extracted_audio_lifetime = pickle.loads(self.__redis.get("extracted_audio_lifetime"))
            res =  foo(self, *args, **kwargs)
            self.__redis.set("extracted_audio_lifetime", pickle.dumps(self.__extracted_audio_lifetime))
            return res
        return fooer
    
    @_synchronise_data
    def get_wav_from_video(self, video_path):
        video = moviepy.editor.VideoFileClip(video_path)
        saved_dir = os.path.join(self.__extracted_audio_folder, os.path.basename(video_path).split(".")[0] + ".wav")
        self.__extracted_audio_lifetime[video_path] = datetime.now()
        
        if saved_dir in self.__extracted_audio_lifetime.keys():
            return saved_dir
        
        video.audio.write_audiofile(saved_dir)
        return saved_dir
    
    # TODO: add to scheduler
    @_synchronise_data
    def delete_expired_wav_lifetimes(self):
        for file_source, current in self.__extracted_audio_lifetime.items():
            if datetime.now() - current > timedelta(seconds=self.__wav_lifetime):
                os.remove(file_source)
                self.__extracted_audio_lifetime.pop(file_source, None)
        
    