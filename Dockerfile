FROM debian:trixie
RUN echo 'deb http://deb.debian.org/debian trixie-backports main' > /etc/apt/sources.list.d/backports.list

RUN apt-get update -y
RUN apt-get install caddy python3-flask python3-waitress -y

COPY . /opt/webapp

EXPOSE 80/tcp
EXPOSE 443/tcp

CMD ["bash", "/opt/webapp/runserver.sh"]