FROM ghcr.io/linuxserver/baseimage-ubuntu:jammy as base

RUN \
  apt-get -qq update && \
  apt-get -y -q install \
    python3-pip \
    libfribidi-dev \
    libharfbuzz-dev \
    libjpeg-dev \
    liblcms2-dev \
    libffi-dev \
    libtool \
    git \
    cmake \
    nasm \
    libaom-dev

RUN \
  python3 -m pip install --upgrade pip

RUN \
  python3 -m pip install Pillow==9.3.0

FROM base as build_test

COPY . /pillow_heif

ARG BUILD_TYPE
RUN \
  if [ `getconf LONG_BIT` = 64 ]; then \
    python3 -m pip install -v "pillow_heif/.[tests]"; \
  else \
    python3 -m pip install -v "pillow_heif/.[tests-min]"; \
  fi && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export EXP_PH_LIBHEIF_VERSION="" && \
  export $BUILD_TYPE && \
  pytest -s pillow_heif && \
  echo "**** Test Done ****"
