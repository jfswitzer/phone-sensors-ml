FROM python:3.12

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
  ffmpeg

RUN pip install --upgrade pip
RUN pip install -e .
