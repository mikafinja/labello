FROM python:3.10-slim AS base_image

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM base_image AS builder
RUN apt-get update && \
    apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    yarnpkg curl build-essential && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
COPY src/package.json src/yarn.lock ./
RUN poetry install --no-dev && \
    yarnpkg install 

FROM base_image as production
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y fontconfig gettext curl
COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH
COPY ./src /labello/
COPY --from=builder $PYSETUP_PATH/node_modules /labello/node_modules

ENV LAB_SERVER_PORT=4242 \
    LAB_SERVER_HOST=0.0.0.0 \
    LAB_LOGGING=30 \
    LAB_WEBSITE_HTML_TITLE="labello - print all your labels" \
    LAB_WEBSITE_TITLE="labello" \
    LAB_WEBSITE_SLUG="print all your labels" \
    LAB_WEBSITE_BOOTSTRAP_LOCAL=True \
    LAB_LABEL_MARGIN_TOP=24 \
    LAB_LABEL_MARGIN_BOTTOM=24 \
    LAB_LABEL_MARGIN_LEFT=24 \
    LAB_LABEL_MARGIN_RIGHT=24 \
    LAB_LABEL_FEED_MARGIN=16 \
    LAB_LABEL_FONT_SPACING=13 \
    LAB_PRINTER_DEVICE="tcp://127.0.0.1:9100" \
    LAB_PRINTER_MODEL="QL-720NW" \
    LAB_FONT_PATH="/opt/labello/fonts"

WORKDIR /labello/
VOLUME /opt/labello/fonts

ENTRYPOINT ["/bin/sh", "/labello/entrypoint.sh"]
