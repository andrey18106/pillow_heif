FROM ghcr.io/linuxserver/baseimage-ubuntu:focal

COPY . /pillow_heif

RUN \
  apt-get update && \
  apt-get install -y \
    python3-pip \
    libfribidi-dev \
    libharfbuzz-dev \
    libjpeg-dev \
    liblcms2-dev \
    libffi-dev \
    libtool \
    git \
    cmake && \
  python3 -m pip install --upgrade pip && \
  echo "**** Install python build dependencies ****" && \
  python3 -m pip install cffi && \
  echo "**** Start building ****" && \
  cd pillow_heif && \
  python3 setup.py bdist_wheel && \
  echo "**** Repairing wheel ****" && \
  python3 -m pip install auditwheel && \
  auditwheel repair -w repaired_dist/ dist/pillow_heif-0.4.0-cp36-abi3-linux_armv7l.whl && \
  echo "**** Testing wheel ****" && \
  echo "**** Build Done ****" && \
  ls -la && ls -la dist && ls -la repaired_dist
