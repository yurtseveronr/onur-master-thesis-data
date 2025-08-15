FROM node:22-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY consumer.js ./

EXPOSE 3000

CMD ["node", "consumer_api.js"]
