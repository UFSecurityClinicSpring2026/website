FROM debian:trixie
RUN echo 'deb http://deb.debian.org/debian trixie-backports main' > /etc/apt/sources.list.d/backports.list

RUN apt-get update -y
RUN apt-get install caddy -y

COPY ./startproxy.sh.gz /tmp

VOLUME ["/opt/caddy"]

RUN gunzip /tmp/startproxy.sh.gz

EXPOSE 80/tcp
EXPOSE 443/tcp

CMD ["bash", "/tmp/startproxy.sh"]