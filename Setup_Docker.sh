#!/bin/sh
sudo docker build -t "webserver:latest" .
sudo docker image prune
sudo docker container rm -f APIServer
sudo docker container rm -f WebServer
sudo docker run --detach --publish 8081:8081 --name APIServer --restart always webserver:latest /bin/sh -c 'cd /WebServer; python3 API_Server.py'
sudo docker run --detach --publish 80:80 --name WebServer --restart always webserver:latest /bin/sh -c 'cd /WebServer; python3 Web_Server.py'