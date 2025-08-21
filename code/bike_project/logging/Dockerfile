FROM python:3.9-slim

RUN apt update && \
    apt install -y cron

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

COPY cronjob /etc/cron.d/cronjob

RUN chmod 0644 /etc/cron.d/cronjob

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD ["cron && tail -f /var/log/cron.log"]