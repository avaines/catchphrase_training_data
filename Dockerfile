FROM python:3.11
WORKDIR /usr/src/app

ADD "game" ./game

# CV2 depdencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install --no-cache-dir -r game/requirements.txt

CMD [ "python", "./game/main.py" ]
