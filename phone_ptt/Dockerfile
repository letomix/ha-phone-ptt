ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
    apk add --no-cache \
    python3 \
    py3-pip \
    py3-fastapi \
    py3-uvicorn \
    py3-requests

WORKDIR /app
COPY app/ /app/
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
