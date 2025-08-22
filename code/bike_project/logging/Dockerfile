FROM continuumio/miniconda3

# installing cron 
RUN apt update && \
    apt install -y cron 

# copying and creating specific conda environment
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml 

# making working directory and moving files to it
WORKDIR /usr/src/app
COPY ./bike_logs.py /usr/src/app/bike_logs.py 
COPY ./run_python_job.sh /usr/src/app/run_python_job.sh

# making scripts and cronjob executable for cron
RUN chmod +x /usr/src/app/bike_logs.py /usr/src/app/run_python_job.sh
COPY cronjob /etc/cron.d/cronjob    
RUN chmod 0644 /etc/cron.d/cronjob

# making log file for cronjob
RUN touch /var/log/cron.log

# linux has issues passing .env to cronjob and this is the workaround
# also executing the cronjob
CMD printenv >> /etc/environment && cron -f