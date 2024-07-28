FROM alpine:3.19.1

WORKDIR /app

RUN apk add git make g++ gcc cmake libarrow elfutils-dev
RUN apk add --repository=https://dl-cdn.alpinelinux.org/alpine/v3.16/main/ libexecinfo-dev libexecinfo

RUN git clone https://github.com/ggerganov/llama.cpp --branch b3440

WORKDIR /app/llama.cpp

RUN make

COPY ./entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

CMD [ "/app/entrypoint.sh" ]