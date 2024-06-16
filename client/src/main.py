import pyaudio
import numpy as np
import requests
import webrtcvad
from scipy.io.wavfile import write
import scipy.signal as sps

import time

import os

SAMPLE_RATE=int(os.environ.get("SAMPLE_RATE"))

CHUNK_SIZE=int(SAMPLE_RATE*0.02)

DEVICE_MIC_ID=int(os.environ.get("DEVICE_MIC_ID"))

DEVICE_SPEAK_ID=int(os.environ.get("DEVICE_SPEAK_ID"))

MAX_BUFFER_SIZE=480000

AUDIO_BUFFER_PATH="/app/files/audio.wav"

STT_URL = "http://stt:8080/inference"

class Microphone:
    def __init__(self,chunk,format=pyaudio.paInt16,channels=1,rate=SAMPLE_RATE,id=DEVICE_MIC_ID):

        '''init input audio device'''
        self.audio=pyaudio.PyAudio()
        self.open_stream(format,channels,rate,chunk,id)

        '''vad initialization'''

        self.vad=webrtcvad.Vad()
        self.vad.set_mode(2)

    '''Change vad aggresive level'''
    def vad_mode(self,mode):
        self.vad.set_mode(mode)

    '''Reopen a stream with different settings'''
    def open_stream(self,format,channels,rate,chunk,id=0):

        self.close_stream()

        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.id = id

        self.stream=self.audio.open(format=format, channels=channels,rate=rate,frames_per_buffer=chunk,input=True,input_device_index=id)
        self.chunk=chunk

    '''Get a chunk then check if it has a voice , if it is true it return a array with chunk else it returns None '''
    def get(self):
        frame=self.stream.read(self.chunk,exception_on_overflow = False)

        if self.vad.is_speech(frame,self.rate):
            print("Speech detected in frame")
            return np.frombuffer(frame,dtype=np.int16)

        return None

    '''Close current stream'''
    def close_stream(self):
        if hasattr(self,'stream'):
            self.stream.stop_stream()
            self.stream.close()

    '''Close microphone completely'''
    def close(self):
        self.close_stream()
        self.audio.terminate()

class Speaker:

    def __init__(self,chunk,format=pyaudio.paInt16,channels=1,rate=SAMPLE_RATE,id=DEVICE_SPEAK_ID):

        self.audio=pyaudio.PyAudio()
        self.open_stream(format,channels,rate,chunk,id)

    def open_stream(self,format,channels,rate,chunk,id=0):

        self.close_stream()

        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.id = id

        self.stream=self.audio.open(format=format, channels=channels,rate=rate,frames_per_buffer=chunk,output=True,output_device_index=id)
        self.chunk=chunk

    def put(self,sample:np.array):
        self.stream.write(sample,len(sample),exception_on_overflow = False)

    '''Close current stream'''
    def close_stream(self):
        if hasattr(self,'stream'):
            self.stream.stop_stream()
            self.stream.close()

    '''Close speaker completely'''
    def close(self):
        self.close_stream()
        self.audio.terminate()


class AudioBuffer:
    
    def __init__(self,max_size:int) -> None:
        self.max_size=max_size
        self.buffer=np.array([])
        
    def push(self,audio:np.ndarray):
        
        if len(audio)+len(self.buffer) >= self.max_size:
            self.buffer=self.buffer[:-len(audio)]
            
        self.buffer=np.append(self.buffer,audio)
        
    
    def get_buffer(self):
        return self.buffer
    
    def clear(self):
        self.buffer=np.array([])


def resample_to_16(clip):
    
    number_of_samples = round(len(clip) * float(16000) / SAMPLE_RATE)

    clip = sps.resample(clip, number_of_samples).astype(np.int16)

    return clip

mic=Microphone(CHUNK_SIZE)

speaker=Speaker(CHUNK_SIZE)    

audio_buffer=np.array([]).astype(np.int16)

recording=False
        
        
while True:
    
    # get audio sample
    audio_input=mic.get()
    
    if audio_input is not None and len(audio_buffer)<MAX_BUFFER_SIZE:
        recording=True
        # append to audio buffer
        audio_buffer = np.append(audio_buffer,audio_input)
    elif recording:
        recording=False
        # push everything into wav file in ram disk
        
        buffer = audio_buffer.astype(np.int16)
        
        
        
        buffer = resample_to_16(buffer)

        audio_length = int(len(buffer)*1000/16000)
        
        if audio_length < 1000:
            frames_to_add = 1000 - audio_length
            
            dummy_buff = np.zeros(int((frames_to_add+10/1000)*16000)).astype(np.int16)
            
            buffer = np.append(buffer,dummy_buff)
            
                
        write('/app/files/sample.wav', 16000, buffer)
        
        audio_buffer=np.array([]).astype(np.int16)
        
        stt_files  = {'file': open('/app/files/sample.wav', 'rb')} 
        
        form = {
            "temperature":"0.0",
            "temperature_inc":"0.2",
            "response_format":"json"
        }
        
        stt_response = requests.post(STT_URL,files = stt_files,data = form)
        
        print(stt_response.status_code)
        print(stt_response.text)
        # run Speech to Text
                
        # run chatbot
        
        # run piper tts
        
        # play sample