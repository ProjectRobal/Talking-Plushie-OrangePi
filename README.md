# IA Talk

An project of making talking plushie driven by LLM model. Now it is running on Orange Pi Zero 2W computer with 4GB on board and ReSpeaker HAT with 2 microphones.

## Used containers:
- chat - a container with a LLM model
- client - a container that use Text to Speech to turn output from chat container into speech
- stt - a container used for converting speech to text, which is then send to chat container

## Used software:
- piper tts - a text to speech software - https://github.com/rhasspy/piper
- whisper.cpp - an implementation of speech to text model in C++ - https://github.com/ggerganov/whisper.cpp
- llama.cpp - written in C++, software for running popular LLM - https://github.com/ggerganov/llama.cpp

## Used models:
- Text to Speech: en_US-amy-low from piper - https://github.com/rhasspy/piper/blob/master/VOICES.md
- LLM: tinyllama-1.1b chat Q4_0 - https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF
- Speech to Text: Whisper Tiny - https://huggingface.co/openai/whisper-tiny

To use models you have to download them and put them in models subfolders and then open compose.yml file and into volumes put 
- - ./< container name >/models/< model name with extension >:/app/models/model.gguf

You need to have docker with docker compose installed onto device obviously after you get it you have to type docker compose build in terminal while beging 
in project directory, then after a while type docker compose up to run containers or docker compose up -d to run it into background.

Initial LLM prompt is located in chatbot/prompt.txt file. Feel free to modify it.

## Miscellaneous

In driver directory I put script written in python to setup audio codec on board of the HAT module, it should be run on computer boot.
In dts folder I put dts file used for setup I2S audio driver required by HAT. To run script on bo!
ard I am using lines similar to in driver/rc.local.


## Pictures:
<p align="center">
  
<img src="https://github.com/user-attachments/assets/50500371-5b84-4d69-a6c8-6592ff9bd357" width="200" height="400" />

<img src="https://github.com/user-attachments/assets/f25b0278-ed41-4ac2-bc32-8e1ffb67dc44" width="200" height="400" />

<img src="https://github.com/user-attachments/assets/7a24128f-bd5b-4788-81a7-3f7d6b18fb14" width="200" height="400" />

</p>

<p align="center">

<img src="https://github.com/user-attachments/assets/cc82e296-e3a6-4706-a611-9ec3e56f0ced" height="400" />

</p>

<p align="center">
Plushie with my creations at Opolcon 2024 in Opole, Poland.
</p>

## Video demo:

https://github.com/user-attachments/assets/3681f490-9656-416c-a514-5403f00ed4fd

