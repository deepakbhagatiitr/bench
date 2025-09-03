FROM apex_arena:base

USER root
RUN apt-get update && apt-get install -y python3 python3-pip
RUN uv pip install --system pandas numpy

WORKDIR /workdir

COPY ./data /workdir/data
COPY tests/ /tests

USER root

