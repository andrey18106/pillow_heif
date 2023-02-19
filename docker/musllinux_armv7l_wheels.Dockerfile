ARG PYTHON_VERSION

FROM python:$PYTHON_VERSION-alpine3.15

COPY . /pillow_heif

RUN \
  apk add --no-cache \
    libtool \
    perl \
    alpine-sdk \
    cmake \
    autoconf \
    automake \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev

RUN \
  echo "**** Installing patchelf ****" && \
  git clone -b 0.17.2 https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make check && make install && \
  cd ..

RUN \
  echo "**** Install python build dependencies ****" && \
  python3 -m pip install wheel && \
  python3 -m pip install pytest Pillow && \
  echo "**** Start building ****" && \
  cd pillow_heif && \
  python3 setup.py bdist_wheel && \
  echo "**** Repairing wheel ****" && \
  PTAG=$(echo $PYTHON_VERSION | tr -d '.' | tr -d '"') && \
  python3 -m pip install auditwheel && \
  python3 -m auditwheel repair -w repaired_dist/ dist/*cp$PTAG*musllinux*.whl && \
  echo "**** Testing wheel ****" && \
  python3 -m pip install repaired_dist/*cp$PTAG*musllinux*.whl && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3 -m pytest -rs && \
  echo "**** Build Done ****"
