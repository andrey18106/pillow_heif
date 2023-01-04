FROM alpine:3.17 as base

RUN \
  apk add --no-cache \
    python3-dev \
    py3-pip \
    perl \
    alpine-sdk \
    libffi-dev \
    cmake \
    nasm \
    aom-dev \
    py3-numpy \
    py3-pillow \
    py3-cffi

RUN \
  python3 -m pip install --upgrade pip

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
