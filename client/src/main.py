import pyaudio
import numpy as np
import requests
import webrtcvad
from piper.voice import PiperVoice

from scipy.io.wavfile import write
import scipy.signal as sps

from fastembed import TextEmbedding

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct

import json

import os


SAMPLE_RATE=int(os.environ.get("SAMPLE_RATE"))

CHUNK_SIZE=int(SAMPLE_RATE*0.02)

DEVICE_MIC_ID=int(os.environ.get("DEVICE_MIC_ID"))

DEVICE_SPEAK_ID=int(os.environ.get("DEVICE_SPEAK_ID"))

MAX_BUFFER_SIZE=480000

AUDIO_BUFFER_PATH="/app/files/audio.wav"

STT_URL = "http://stt:8080/inference"

CHATBOT_URL = "http://chat:8080/completion"

SYSTEM_PROMPT = "You are famous Vocaloid called IA. Your sister is another vocaloid called ONE. You come from a planet ARIA."

class Microphone:
    def __init__(self,chunk,format=pyaudio.paInt16,channels=1,rate=SAMPLE_RATE,id=DEVICE_MIC_ID):

        '''init input audio device'''
        self.audio=pyaudio.PyAudio()
        self.open_stream(format,channels,rate,chunk,id)

        '''vad initialization'''

        self.vad=webrtcvad.Vad()
        self.vad.set_mode(3)

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
        self.stream.write(sample,len(sample))

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

    clip = sps.resample(clip, number_of_samples)

    return clip.astype(np.int16)

def resample_from_to(clip,input_sample_rate,output_sample_rate):
    
    number_of_samples = round(len(clip) * float(output_sample_rate) / input_sample_rate)
    
    print("Resample to: ",number_of_samples)

    clip = sps.resample(clip, number_of_samples)

    return clip.astype(np.int16)


model = TextEmbedding(model_name="mixedbread-ai/mxbai-embed-large-v1")
    
qdrant = QdrantClient("http://rag:6333")


def retrive_arguments(prompt):
    output=""
    
    query_vector=next(model.embed(prompt))
    
    search_result = qdrant.search(
    collection_name="ia",
    query_vector=query_vector,
    limit=5
    )
    
    for result in search_result:
        payload = result.payload
        output+=payload["text"]
        
    return output


def create_prompt(prompt):
    
    return "SYSTEM:{}\nUSER:{}\nIA:".format(SYSTEM_PROMPT+retrive_arguments(prompt),prompt)


mic=Microphone(CHUNK_SIZE)


tts = PiperVoice.load("/app/tts/model.onnx")

print("Voice configs:")
print(tts.config)

speaker=Speaker(SAMPLE_RATE)#,rate=tts.config.sample_rate)    

audio_buffer=np.array([]).astype(np.int16)

recording=False

if os.path.exists('/app/files/sample.wav'):
    print("Found old buffor removing it!")
    os.remove('/app/files/sample.wav')

if not os.path.exists('/app/files'):
    os.mkdir('/app/files')
        
print("Starting service")

message=""

while True:
    
    # get audio sample
    audio_input=mic.get()
        
    if audio_input is not None and len(audio_buffer)<MAX_BUFFER_SIZE:
        recording=True
        # append to audio buffer
        audio_buffer = np.append(audio_buffer,audio_input)
        print("Append audio to buffer!")
    elif recording:
        recording=False
        # push everything into wav file in ram disk
        print("Sending everything to chatbot!")
        
        buffer = audio_buffer.astype(np.int16)
        
        buffer = resample_to_16(buffer)

        audio_length = int(len(buffer)*1000/16000)
        
        if audio_length < 1000:
            frames_to_add = 1000 - audio_length
            
            dummy_buff = np.zeros(int(((frames_to_add+10)/1000)*16000)).astype(np.int16)
            
            buffer = np.append(buffer,dummy_buff)
                            
        write('/app/files/sample.wav', 16000, buffer)
        
        #iter+=1
        
        audio_buffer=np.array([]).astype(np.int16)
        
        stt_files  = {'file': open('/app/files/sample.wav', 'rb')} 
        
        form = {
            "temperature":"0.0",
            "temperature_inc":"0.2",
            "response_format":"json"
        }
        
        # run Speech to Text
        
        stt_response = requests.post(STT_URL,files = stt_files,data = form)
        
        print(stt_response.status_code)
        print(stt_response.text)
        
        if stt_response.status_code != 200:
            continue
        
        prompt_text = json.loads(stt_response.text)["text"]
                
        # run chatbot
        if len(prompt_text)>0:
            
            prompt_data={
                "prompt": create_prompt(prompt_text),
                "stream":True,
                "cache_prompt":True,
                "n_keep":1024,
                "stop":["USER:","ONE:"]
            }
            
            chatbot_response = requests.post(CHATBOT_URL,json = prompt_data,stream=True)
            
            for chunk in chatbot_response.iter_lines(decode_unicode=True):
                if chunk:
                    try:
                        chunk = chunk[5:]
                        frame = json.loads(chunk)
                        message+=frame["content"]
                    
                        if frame["content"] == '\n' or frame["stop"]:
                            print(message)
                            # play message and run piper tts
                            #tts_queue.put(message)
                            for audio in tts.synthesize_stream_raw(message):
                                audio_int = np.frombuffer(audio,dtype=np.int16)
                                
                                audio_out = resample_from_to(audio_int,tts.config.sample_rate,SAMPLE_RATE)
            
                                speaker.put(audio_out)
                            message=""
                    except Exception as e:
                        print(str(e))