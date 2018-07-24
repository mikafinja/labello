#!/bin/sh

if [ "$LABELLO_DOWNLOAD_FONT" = "yes" ] || [ "$1" = "download_font" ]; then
    mkdir -p /opt/labello/download_font
    wget https://github.com/googlefonts/spacemono/raw/master/fonts/SpaceMono-Regular.ttf -O /opt/labello/download_font/Space-Mono.ttf
fi

/usr/bin/python3 /opt/labello/src/labello.py