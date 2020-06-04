FROM ubuntu:18.04
COPY . /app
RUN apt-get update && apt-get install -y \
	sox
#	gnustep-gui-runtime\
#	pulseaudio socat\
#	alsa-utils\
#	ffmpeg
RUN ./hello_world.sh
