FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/djerfy/chiadog"
LABEL org.opencontainers.image.description="Chiadog is a monitoring tool for Chia nodes and farms."
LABEL org.opencontainers.image.licenses="MIT"

ENV CHIADOG_CONFIG_DIR=/root/.chiadog/config.yaml
ENV TZ=UTC

WORKDIR /chiadog

COPY requirements.txt /chiadog

RUN python3 -m venv venv && \
    . ./venv/bin/activate && \
    pip3 install -r requirements.txt

COPY . /chiadog

ENTRYPOINT ["/chiadog/entrypoint.sh"]
