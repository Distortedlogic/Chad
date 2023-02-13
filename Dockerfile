# syntax = docker/dockerfile:experimental
FROM jupyter/minimal-notebook
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential graphviz-dev graphviz \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir pyparsing pydot
RUN pip install pygraphviz
COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt --cache-dir /root/.cache/pip
WORKDIR /notebooks
COPY . .
RUN chown 1000:100 .
USER 1000
