import noisereduce as nr
from scipy.io import wavfile
import io, os
import numpy as np

from code.settings_manager import SettingsManager
from etc.settings import Settings

class NoiseReduction():
    
    
    def __init__(self) -> None:
        self.__settings_manager = SettingsManager()
        self.__reduced_noise_files = Settings.reduced_noise_files.value
    
    def stationary_noise_reduction(self, audio_file):
        stationary = self.__settings_manager.get_setting("prefer_stationary_noise_reduction")
        try:
            try:
                return self.__short_form_noise_reduction(audio_file, stationary = stationary)
            except Exception:
                return self.__short_form_noise_reduction(audio_file, stationary = False)
        except Exception:
            try:
                return self.__long_form_noise_reduction(audio_file, stationary = stationary)
            except Exception:
                return self.__long_form_noise_reduction(audio_file, stationary = False)
    
    def __short_form_noise_reduction(self, audio_file, stationary = False):
        """noise reduction on mono audio files.

        Args:
            audio_file (str): loc of audio.

        Returns:
            str: loc of edited file.
        """
        # load data
        rate, data = wavfile.read(audio_file)
        
        # perform noise reduction
        reduced_noise = nr.reduce_noise(y=data, sr=rate, stationary=stationary)
        
        loc = os.path.join(self.__reduced_noise_files, os.path.basename(audio_file))
        if os.path.isfile(loc):
            os.remove(loc)
        wavfile.write(loc, rate, reduced_noise)
        return loc
    
    def __long_form_noise_reduction(self, audio_file, stationary = False):
        """Works when audio is not mono.

        Args:
            audio_file (str): loc of audio.

        Returns:
            str: loc of edited file.
        """
        rate, data = wavfile.read(audio_file)
        data1 = data[:,0]
        data2 = data[:,1]
        
        # noise reduction
        reduced_noise1 = nr.reduce_noise(y=data1, sr=rate, stationary=stationary)
        reduced_noise2 = nr.reduce_noise(y=data2, sr=rate, stationary=stationary)
        reduced_noise = np.stack((reduced_noise1, reduced_noise2), axis=1)
        
        loc = os.path.join(self.__reduced_noise_files, os.path.basename(audio_file))
        if os.path.isfile(loc):
            os.remove(loc)
        wavfile.write(loc, rate, reduced_noise)
        return loc
    

    
    