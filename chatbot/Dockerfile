FROM alpine:3.19.1

WORKDIR /app

RUN apk add git make g++ cmake libarrow

RUN git clone https://github.com/ggerganov/llama.cpp

WORKDIR /app/llama.cpp

RUN make

COPY ./entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

CMD [ "/app/entrypoint.sh" ]