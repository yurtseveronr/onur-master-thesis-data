FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ENV PORT=8084
ENV OMDB_API_KEY=457e93fc
ENV OMDB_BASE_URL=http://www.omdbapi.com/
ENV AWS_REGION=eu-central-1
ENV DYNAMODB_MOVIE_TABLE=movies
ENV DYNAMODB_SERIES_TABLE=TVSeries

EXPOSE 8084

CMD ["npx", "ts-node", "src/app.ts"]
