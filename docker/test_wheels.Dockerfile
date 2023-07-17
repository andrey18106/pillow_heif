ARG BASE_IMAGE
FROM $BASE_IMAGE

ARG PREPARE_CMD
RUN $PREPARE_CMD
ARG INSTALL_CMD
RUN $INSTALL_CMD

RUN python3 -m pip install --upgrade --break-system-packages \
    pip || echo "pip upgrade failed"
RUN python3 -m pip install --prefer-binary --break-system-packages \
    pillow
RUN python3 -m pip install --break-system-packages \
    pytest numpy pympler defusedxml

ARG EX_ARG
RUN python3 -m pip install $EX_ARG --break-system-packages --no-deps --only-binary=:all: pillow_heif

COPY . /pillow_heif

ARG TEST_TYPE
RUN $TEST_TYPE && \
    python3 -m pytest -v pillow_heif/. && \
    echo "**** Test Done ****" && \
    python3 -m pip show pillow_heif
