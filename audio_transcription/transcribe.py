import whisper
import librosa
import math
import os
import multiprocessing
import pickle
import threading
import string
import random
from pydub import AudioSegment
import torch

from code.audio.modules.noise_reduction import NoiseReduction
from etc.settings import Settings
from code.settings_manager import SettingsManager
from code.redis_connection import RedisConnection

split_audio_dirs = Settings.split_audio_dirs.value

class AutoTranscription():
    __instance = None
    __model = whisper.load_model("base")
    __noise_reduction = None
    __settings = SettingsManager()
    __redis = RedisConnection().redis
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__noise_reduction = NoiseReduction()
            
        return cls.__instance
    
    @classmethod
    def transcribe(cls, audio_file, job_id = "test"):
        y, sr = librosa.load(audio_file)
        duration = librosa.get_duration(y, sr) * 1000 # in milliseconds
        split = cls.__settings.get_setting("transcription_split") * 1000 # in milliseconds
        
        if split * 1.2 > duration :
            result = cls.__model.transcribe(audio_file)
            return result["text"]
        else:
            results = []
            folder = cls.split_audio(audio_file, duration=duration, split=split, job_id=job_id)
            items = os.listdir(folder)
            items.sort()
            
            threads = []
            ctx = multiprocessing.get_context('spawn')
            keys = []
            
            for item in items:
                global url, key
                url = os.path.join(folder, item)
                url_key = cls.id_generator()
                keys.append(url_key)
                print(f"Key: {url_key} || Item: {url}")
                p = ctx.Process(target=cls.process_transcription, args=(url, url_key,))
                threads.append(p)
                
            [p.start() for p in threads]
            [p.join() for p in threads]
            
            for key in keys:
                res = cls.__redis.get(key)
                results.append(res)
                
            #TODO:  delete the used folder after use + delete the used redis variable.
                
            return results
            
    @classmethod
    def id_generator(cls, size=10):
        valid = False
        while not valid:
            key_id =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))
            if cls.__redis.exists(key_id) == 0:
                valid = True
        return key_id
        
    @classmethod
    def split_audio(cls, audio_file, duration=None, split=None, job_id = "test"):
        if duration is None:
            y, sr = librosa.load(audio_file)
            duration = librosa.get_duration(y, sr) * 1000 # in milliseconds
        if split is None:
            split = cls.__settings.get_setting("transcription_split")
            
        audio = AudioSegment.from_wav(audio_file)
        
        base_dir = split_audio_dirs
        print(f"Base dir: {base_dir} || Job ID: {job_id}")
        base_dir = os.path.join(base_dir, job_id)
        print(os.path.isdir(base_dir))
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
            
        progress:float = 0.0
        number_of_splits = math.floor(duration / split)
        max_reps = 0
        
        for item in  range(number_of_splits):
            name = os.path.join(base_dir, f"{item}.wav")
            print(f"File Loc: {name}")
            max_reps = item
            if os.path.isfile(name):
                os.remove(name)
                
            if item == 0:
                a0 = audio[:split]
                a0.export(name, format="wav")
                progress = split
            else:
                audio_segment = audio[progress:progress + split]
                audio_segment.export(name, format="wav")
                progress += split
        max_reps += 1
        name = os.path.join(base_dir, f"{max_reps}.wav")
        audio_segment = audio[progress:duration]
        audio_segment.export(name, format="wav")
        return base_dir
        
    @classmethod
    def process_transcription(cls, file, key):
        torch.cuda.init()
        result = cls.__model.transcribe(file)
        cls.__redis.set(key, result["text"])
            
