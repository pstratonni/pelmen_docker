
FROM python:3.9-alpine3.18

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /server

#RUN apk add postgresql-client build-base postgresql-dev
RUN apk update \
    && apk add gcc python3-dev musl-dev freetype-dev postgresql-client build-base postgresql-dev

COPY requirements.txt /temp/requiremets.txt
RUN pip install -r /temp/requiremets.txt

RUN adduser pfunt --disabled-password
USER pfunt

EXPOSE 8000

COPY server /server

ENTRYPOINT ["/server/entrypoint.sh"]


