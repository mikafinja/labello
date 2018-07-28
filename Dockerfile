FROM alpine:latest
WORKDIR /opt/labello
COPY . /opt/labello
RUN apk upgrade -U && \
    apk add python3 py-pillow fontconfig yarn && \
    pip3 install -r requirements_docker.txt && \
    yarn && \
    mkdir /opt/labello/fonts
EXPOSE 4242
VOLUME /opt/labello/fonts
ENTRYPOINT ["/bin/sh", "/opt/labello/entrypoint.sh"]

