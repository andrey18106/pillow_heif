FROM debian:buster-slim

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
    wget \
    build-essential \
    cmake \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libsqlite3-dev \
    libbz2-dev

RUN \
  echo "**** Installing patchelf ****" && \
  git clone -b 0.17.2 https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make check && make install && \
  cd ..

RUN \
  echo "**** Python3.7: Install python build dependencies ****" && \
  python3 -m pip install --upgrade pip && \
  python3 -m pip install wheel && \
  python3 -m pip install pytest Pillow \
  echo "**** Python3.7: Start building ****" && \
  cd pillow_heif && \
  python3 setup.py bdist_wheel && \
  echo "**** Python3.7: Repairing wheel ****" && \
  python3 -m pip install auditwheel && \
  python3 -m auditwheel repair -w repaired_dist/ dist/*cp37*.whl --plat manylinux_2_28_armv7l && \
  echo "**** Python3.7: Testing wheel ****" && \
  python3 -m pip install repaired_dist/*cp37*.whl && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3 -m pytest -rs && \
  echo "**** Python3.7: Build Done ****"

RUN \
  PYTHON_VER=3.8.16 && \
  echo "**** Python3.8: Install python ****" && \
  wget https://www.python.org/ftp/python/$PYTHON_VER/Python-$PYTHON_VER.tgz && \
  tar -xf Python-$PYTHON_VER.tgz && rm Python-$PYTHON_VER.tgz && \
  cd Python-$PYTHON_VER && \
  ./configure --enable-optimizations && \
  make altinstall && \
  cd .. && rm -rf Python-$PYTHON_VER && \
  echo "**** Python3.8: Install python build dependencies ****" && \
  python3.8 -m pip install --upgrade pip && \
  python3.8 -m pip install wheel && \
  python3.8 -m pip install pytest Pillow \
  echo "**** Python3.8: Start building ****" && \
  cd pillow_heif && \
  python3.8 setup.py bdist_wheel && \
  echo "**** Python3.8: Repairing wheel ****" && \
  python3.8 -m pip install auditwheel && \
  python3.8 -m auditwheel repair -w repaired_dist/ dist/*cp38*.whl --plat manylinux_2_28_armv7l && \
  echo "**** Python3.8: Testing wheel ****" && \
  python3.8 -m pip install repaired_dist/*cp38*.whl && \
  python3.8 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3.8 -m pytest -rs && \
  echo "**** Python3.8: Build Done ****"

RUN \
  PYTHON_VER=3.9.16 && \
  echo "**** Python3.9: Install python ****" && \
  wget https://www.python.org/ftp/python/$PYTHON_VER/Python-$PYTHON_VER.tgz && \
  tar -xf Python-$PYTHON_VER.tgz && rm Python-$PYTHON_VER.tgz && \
  cd Python-$PYTHON_VER && \
  ./configure --enable-optimizations && \
  make altinstall && \
  cd .. && rm -rf Python-$PYTHON_VER && \
  echo "**** Python3.9: Install python build dependencies ****" && \
  python3.9 -m pip install --upgrade pip && \
  python3.9 -m pip install wheel && \
  python3.9 -m pip install pytest Pillow \
  echo "**** Python3.9: Start building ****" && \
  cd pillow_heif && \
  python3.9 setup.py bdist_wheel && \
  echo "**** Python3.9: Repairing wheel ****" && \
  python3.9 -m pip install auditwheel && \
  python3.9 -m auditwheel repair -w repaired_dist/ dist/*cp39*.whl --plat manylinux_2_28_armv7l && \
  echo "**** Python3.9: Testing wheel ****" && \
  python3.9 -m pip install repaired_dist/*cp39*.whl && \
  python3.9 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3.9 -m pytest -rs && \
  echo "**** Python3.9: Build Done ****"

RUN \
  PYTHON_VER=3.10.9 && \
  echo "**** Python3.10: Install python ****" && \
  wget https://www.python.org/ftp/python/$PYTHON_VER/Python-$PYTHON_VER.tgz && \
  tar -xf Python-$PYTHON_VER.tgz && rm Python-$PYTHON_VER.tgz && \
  cd Python-$PYTHON_VER && \
  ./configure --enable-optimizations && \
  make altinstall && \
  cd .. && rm -rf Python-$PYTHON_VER && \
  echo "**** Python3.10: Install python build dependencies ****" && \
  python3.10 -m pip install --upgrade pip && \
  python3.10 -m pip install wheel && \
  python3.10 -m pip install pytest Pillow \
  echo "**** Python3.10: Start building ****" && \
  cd pillow_heif && \
  python3.10 setup.py bdist_wheel && \
  echo "**** Python3.10: Repairing wheel ****" && \
  python3.10 -m pip install auditwheel && \
  python3.10 -m auditwheel repair -w repaired_dist/ dist/*cp310*.whl --plat manylinux_2_28_armv7l && \
  echo "**** Python3.10: Testing wheel ****" && \
  python3.10 -m pip install repaired_dist/*cp310*.whl && \
  python3.10 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3.10 -m pytest -rs && \
  echo "**** Python3.10: Build Done ****"

RUN \
  PYTHON_VER=3.11.1 && \
  echo "**** Python3.11: Install python ****" && \
  wget https://www.python.org/ftp/python/$PYTHON_VER/Python-$PYTHON_VER.tgz && \
  tar -xf Python-$PYTHON_VER.tgz && rm Python-$PYTHON_VER.tgz && \
  cd Python-$PYTHON_VER && \
  ./configure --enable-optimizations && \
  make altinstall && \
  cd .. && rm -rf Python-$PYTHON_VER && \
  echo "**** Python3.11: Install python build dependencies ****" && \
  python3.11 -m pip install --upgrade pip && \
  python3.11 -m pip install wheel && \
  python3.11 -m pip install pytest Pillow \
  echo "**** Python3.11: Start building ****" && \
  cd pillow_heif && \
  python3.11 setup.py bdist_wheel && \
  echo "**** Python3.11: Repairing wheel ****" && \
  python3.11 -m pip install auditwheel && \
  python3.11 -m auditwheel repair -w repaired_dist/ dist/*cp311*.whl --plat manylinux_2_28_armv7l && \
  echo "**** Python3.11: Testing wheel ****" && \
  python3.11 -m pip install repaired_dist/*cp311*.whl && \
  python3.11 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3.11 -m pytest -rs && \
  echo "**** Python3.11: Build Done ****"
