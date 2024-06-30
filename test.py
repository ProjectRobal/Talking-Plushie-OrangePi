import requests
import json

CHATBOT_URL = "http://localhost:8080/completion"

SYSTEM_PROMPT = "You are famous Vocaloid called IA. Your sister is another vocaloid called ONE. You come from a planet ARIA."


def create_prompt(prompt):
    
    return "SYSTEM:{}\nUSER:{}\nIA:".format(SYSTEM_PROMPT,prompt)

prompt_text="Really?"
# run chatbot
if len(prompt_text)>0:
    
    prompt_data={
        "prompt": create_prompt(prompt_text),
        "stream":True,
        "cache_prompt":True,
        "n_keep":1024,
        "stop":["USER:"]
    }
    
    message = ""
    
    chatbot_response = requests.post(CHATBOT_URL,json = prompt_data,stream=True)
    
    for chunk in chatbot_response.iter_lines(decode_unicode=True):
        if chunk:
            chunk = chunk[5:]
            print(chunk)
            frame = json.loads(chunk)
            message+=frame["content"]
            
            if frame["content"] == '\n' or frame["stop"]:
                print(message)
                message=""