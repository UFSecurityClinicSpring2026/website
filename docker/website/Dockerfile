FROM debian:trixie
RUN echo 'deb http://deb.debian.org/debian trixie-backports main' > /etc/apt/sources.list.d/backports.list

RUN apt-get update -y
RUN apt-get install python3-flask python3-waitress -y

COPY ./webapp /opt/webapp/
COPY ./startwebsite.sh.gz /tmp/

VOLUME ["/opt/caddy"]

RUN gunzip /tmp/startwebsite.sh.gz

CMD ["bash", "/tmp/startwebsite.sh"]