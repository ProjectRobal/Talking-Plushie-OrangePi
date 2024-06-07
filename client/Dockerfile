FROM python:3.8.19-alpine3.19

WORKDIR /app

COPY ./src /app

RUN apk add build-base gcc make

RUN apk add git

RUN pip install --upgrade pip

RUN pip3 install -r requirments.txt

COPY ./entrypoint.sh /entrypoint.sh

CMD [ "/entrypoint.sh" ]