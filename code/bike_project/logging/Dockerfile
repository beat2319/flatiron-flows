FROM continuumio/miniconda3

RUN apt update && \
    apt install -y cron


ADD environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc_conda

WORKDIR /usr/src/app

COPY ./bike_logs.py /usr/src/app/bike_logs.py 

COPY cronjob /etc/cron.d/cronjob    

RUN chmod 0644 /etc/cron.d/cronjob

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log