FROM python:3.10-slim

RUN apt update
RUN apt install -y libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx

RUN pip3 install opencv-contrib-python
RUN pip3 install websockets

RUN apt clean

COPY . /app
WORKDIR /app
ENTRYPOINT python3 main.py