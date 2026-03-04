FROM debian:trixie
RUN echo 'deb http://deb.debian.org/debian trixie-backports main' > /etc/apt/sources.list.d/backports.list

RUN apt-get update -y
RUN apt-get install python3-flask python3-waitress cryptsetup -y

COPY ./website /opt/website/
COPY ./startwebsite.sh.gz /opt/
COPY ./setupencryption.sh.gz /opt/

RUN mkdir /opt/website/data
VOLUME ["/opt/website/data"]

RUN gunzip /opt/startwebsite.sh.gz
RUN gunzip /opt/setupencryption.sh.gz
RUN bash /opt/setupencryption.sh

CMD ["bash", "/opt/startwebsite.sh"]