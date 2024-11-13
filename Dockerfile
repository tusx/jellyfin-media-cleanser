FROM docker.io/library/python:3-slim

WORKDIR /usr/src/app

ENV SCRIPT_LOOP_TIME=1800
ENV MOVIE_IGNORE_FAVORITE=0
ENV MOVIE_DELETE_PLAYED=0
ENV MOVIE_DELETE_ADDED_AFTER_N_DAYS=0
ENV MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS=0
ENV SERIES_IGNORE_FAVORITE_EPISODE=0
ENV SERIES_DELETE_PLAYED_EPISODE=0
ENV SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS=0
ENV SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS=0
ENV SERIES_KEEP_LAST_EPISODE=1
ENV PYTHONUNBUFFERED=1

ADD app.py ./

RUN pip install --no-cache-dir requests

CMD [ "python", "./app.py" ]