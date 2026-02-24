FROM debian:trixie
RUN echo 'deb http://deb.debian.org/debian trixie-backports main' > /etc/apt/sources.list.d/backports.list

RUN apt-get update -y
RUN apt-get install python3-flask python3-waitress -y

COPY ./website /opt/website/
COPY ./startwebsite.sh.gz /opt/

RUN gunzip /opt/startwebsite.sh.gz

CMD ["bash", "/opt/startwebsite.sh"]