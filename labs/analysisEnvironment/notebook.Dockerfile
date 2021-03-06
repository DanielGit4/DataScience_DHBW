FROM jupyter/all-spark-notebook:82d1d0bf0867
MAINTAINER geoHeil <georg.heiler@csh.ac.at>

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
RUN jupyter labextension install jupyterlab_bokeh

RUN whoami
USER root
RUN apt-get update && apt-get install -y graphviz
