#!/bin/sh

envsubst < config.local.skel > config.local.yaml

if [ "$LABELLO_DOWNLOAD_FONT" = "yes" ] || [ "$1" = "download_font" ]; then
    mkdir -p /labello/download_font
    curl -L https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf --output-dir /labello/download_font/ --remote-name
    echo '  - /labello/download_font' >> config.local.yaml
fi

gunicorn -w 1 -b $LAB_SERVER_HOST:$LAB_SERVER_PORT labello:app