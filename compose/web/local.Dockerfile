FROM alpine

COPY ./requirements /requirements

RUN apk update && \
    apk upgrade && \
    apk add --update python3 python3-dev git postgresql-client postgresql-dev build-base gettext jpeg-dev zlib-dev && \
    pip3 install --upgrade pip && \
    pip3 install -r /requirements/local.txt && \
    apk del -r python3-dev postgresql git

COPY ./compose/web/local.sh /local.sh
RUN chmod +x /local.sh

COPY ./compose/web/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]