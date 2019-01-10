FROM alpine:latest
WORKDIR /opt/labello
COPY . /opt/labello
RUN apk upgrade -U && \
    apk add python3 py-pillow fontconfig yarn gettext python3-dev g++ && \
    pip3 install -r requirements_docker.txt && \
    yarn --cwd src && \
    mkdir /opt/labello/fonts
VOLUME /opt/labello/fonts
ENV LAB_SERVER_PORT=4242
ENV LAB_SERVER_HOST=0.0.0.0
ENV LAB_LOGGING=30
ENV LAB_WEBSITE_HTML_TITLE="labello - print all your labels"
ENV LAB_WEBSITE_TITLE="labello"
ENV LAB_WEBSITE_SLUG="print all your labels"
ENV LAB_WEBSITE_BOOTSTRAP_LOCAL=True
ENV LAB_LABEL_MARGIN_TOP=24
ENV LAB_LABEL_MARGIN_BOTTOM=24
ENV LAB_LABEL_MARGIN_LEFT=24
ENV LAB_LABEL_MARGIN_RIGHT=24
ENV LAB_LABEL_FEED_MARGIN=16
ENV LAB_LABEL_FONT_SPACING=13
ENV LAB_PRINTER_DEVICE="tcp://127.0.0.1:9100"
ENV LAB_PRINTER_MODEL="QL-720NW"
ENV LAB_FONT_PATH="/opt/labello/fonts"
ENTRYPOINT ["/bin/sh", "/opt/labello/entrypoint.sh"]
