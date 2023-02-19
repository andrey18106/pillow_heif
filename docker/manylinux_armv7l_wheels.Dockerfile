ARG PY_VERSION

FROM python:$PY_VERSION-buster

COPY . /pillow_heif

RUN \
  apt-get update && \
  apt-get install -y \
    libfribidi-dev \
    libharfbuzz-dev \
    libjpeg-dev \
    liblcms2-dev \
    libffi-dev \
    libtool \
    git \
    wget \
    autoconf \
    automake \
    cmake

RUN \
  echo "**** Installing patchelf ****" && \
  git clone -b 0.17.2 https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make check && make install && \
  cd ..

ARG PY_VERSION
RUN \
  echo "**** Install python build dependencies ****" && \
  python3 -m pip install wheel && \
  python3 -m pip install pytest Pillow && \
  echo "**** Start building ****" && \
  cd pillow_heif && \
  python3 setup.py bdist_wheel && \
  echo "**** Repairing wheel ****" && \
  PTAG=$(echo $PY_VERSION | tr -d '.' | tr -d '"') && \
  python3 -m pip install auditwheel && \
  python3 -m auditwheel repair -w repaired_dist/ dist/*-cp$PTAG-*manylinux*.whl --plat manylinux_2_28_armv7l && \
  echo "**** Testing wheel ****" && \
  python3 -m pip install repaired_dist/*-cp$PTAG-*manylinux*.whl && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3 -m pytest -rs && \
  echo "**** Build Done ****"
