FROM continuumio/miniconda3

COPY ./python/bike_logs.py /app/bike_logs.py
WORKDIR /app
ADD environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
