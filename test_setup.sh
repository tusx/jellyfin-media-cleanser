#!/bin/bash

NAME=jellyfin-media-cleanser

docker image rm $NAME-img

docker build -t $NAME-img -f Dockerfile .

docker run -it --rm --name=$NAME $NAME-img

# this .sh file is used by me (tusx) for testing 
