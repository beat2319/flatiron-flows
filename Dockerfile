FROM node:20.10.0-alpine

# Set timezone to Denver
RUN apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/America/Denver /etc/localtime

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["node", "log.js"]