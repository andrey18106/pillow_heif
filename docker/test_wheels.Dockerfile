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
RUN source venv/bin/activate && \
    pip install --upgrade pip || echo "pip upgrade failed" && \
    pip install --prefer-binary pillow && \
    pip install pytest numpy pympler defusedxml && \
    pip install $EX_ARG --no-deps --only-binary=:all: pillow_heif && \
    $TEST_TYPE && \
    pytest -v pillow_heif/. && \
    echo "**** Test Done ****" && \
    pip show pillow_heif
