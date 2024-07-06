FROM python:3.10.14-bullseye

WORKDIR /app

COPY ./src /app

RUN apt update
RUN apt install build-essential gcc make ca-certificates curl git libasound2-dev portaudio19-dev libportaudiocpp0 python-all-dev -y

RUN pip3 install --upgrade pip

RUN pip3 install -r requirments.txt

COPY ./entrypoint.sh /entrypoint.sh

RUN chmod 777 /entrypoint.sh

CMD [ "/entrypoint.sh" ]