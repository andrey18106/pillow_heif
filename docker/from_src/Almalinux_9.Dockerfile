FROM almalinux:9 as base

RUN \
  yum makecache && \
  dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm && \
  yum makecache && \
  yum install -y python3 python3-pip python3-devel libheif-devel

RUN \
  python3 -m pip install --upgrade pip

FROM base as build_test

COPY . /pillow_heif

RUN \
  if [ `getconf LONG_BIT` = 64 ]; then \
    python3 -m pip install -v "pillow_heif/.[tests]"; \
  else \
    python3 -m pip install -v "pillow_heif/.[tests-min]"; \
  fi && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest pillow_heif && \
  echo "**** Test Done ****"
