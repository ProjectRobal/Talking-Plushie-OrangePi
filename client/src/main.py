import pyaudio
import numpy as np
import requests
import webrtcvad
import whisper


CHUNK_SIZE=4096

MAX_BUFFER_SIZE=480000

class Microphone:
    def __init__(self,chunk,format=pyaudio.paInt16,channels=1,rate=16000,id=0):

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

    def __init__(self,chunk,format=pyaudio.paInt16,channels=1,rate=16000,id=0):

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

mic=Microphone(4096)    

audio_buffer=np.array([])

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
        # run Speech to Text model and send it to chatbot