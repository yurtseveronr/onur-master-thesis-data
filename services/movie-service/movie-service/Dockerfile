FROM golang:1.23

ENV AWS_REGION="us-east-1"


WORKDIR /app

COPY go.mod ./
COPY go.sum ./
RUN go mod download



COPY . ./

RUN go build -o movie-service

EXPOSE 8081

CMD ["./movie-service"]
