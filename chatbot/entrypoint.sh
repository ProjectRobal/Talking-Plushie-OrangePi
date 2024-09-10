#!/bin/sh
# Send request on 0.0.0.0:8080/

./llama-server -m /app/models/model.gguf -c 4096 --host 0.0.0.0 --system-prompt-file /app/prompt.txt --keep -1