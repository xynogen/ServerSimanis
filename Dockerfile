FROM python:3.8-buster

COPY . /WebServer

RUN python3 -m pip install -U pip
RUN python3 -m pip install -r /WebServer/requirements.txt
RUN /bin/sh -c 'cd /WebServer; python3 Setup.py'