FROM python:3.9.19-alpine3.19

WORKDIR /app

COPY ./src /app

RUN pip intall -r requirments.txt

COPY ./entrypoint.sh /entrypoint.sh

CMD [ "/entrypoint.sh" ]