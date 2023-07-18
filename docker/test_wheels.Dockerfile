ARG BASE_IMAGE
FROM $BASE_IMAGE

ARG PREPARE_CMD
RUN $PREPARE_CMD
ARG INSTALL_CMD
RUN $INSTALL_CMD

COPY . /pillow_heif

ARG EX_ARG
ARG TEST_TYPE

RUN python3 -m venv venv

RUN \
    venv/bin/python3 -m pip install --upgrade pip || echo "pip upgrade failed" && \
    venv/bin/python3 -m pip install --prefer-binary pillow && \
    venv/bin/python3 -m pip install pytest pympler defusedxml && \
    venv/bin/python3 -m pip install --only-binary=:all: numpy || true && \
    venv/bin/python3 -m pip install $EX_ARG --no-deps --only-binary=:all: pillow_heif && \
    $TEST_TYPE && \
    venv/bin/python3 -m pytest -v pillow_heif/. && \
    echo "**** Test Done ****" && \
    venv/bin/python3 -m pip show pillow_heif
