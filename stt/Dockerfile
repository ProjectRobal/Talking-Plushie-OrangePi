FROM alpine:3.19.1

WORKDIR /app

RUN apk add git make g++ cmake

RUN git clone https://github.com/ggerganov/whisper.cpp.git

WORKDIR /app/whisper.cpp

RUN make

RUN make server

COPY ./entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

CMD [ "/app/entrypoint.sh" ]