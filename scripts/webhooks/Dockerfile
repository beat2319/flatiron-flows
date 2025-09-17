FROM continuumio/miniconda3

# installing cron 
RUN apt update && \
    apt install -y cron 

# copying and creating specific conda environment
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml 

# making working directory and moving files to it
WORKDIR /app
COPY ./send_webhook.py /app/send_webhook.py 
COPY ./run_python_job.sh /app/run_python_job.sh
COPY ./images /app/images

# making scripts and cronjob executable for cron
RUN chmod +x /app/send_webhook.py /app/run_python_job.sh
COPY cronjob /etc/cron.d/cronjob    
RUN chmod 0644 /etc/cron.d/cronjob

# making log file for cronjob
RUN touch /var/log/cron.log

# linux has issues passing .env to cronjob and this is the workaround
# also executing the cronjob
CMD printenv >> /etc/environment && cron -f