FROM golang:1.23

# ✅ ENV Variables for AWS Credentials
ENV AWS_REGION="us-east-1"


WORKDIR /app

# ✅ Copy and Install Dependencies
COPY go.mod ./
COPY go.sum ./
RUN go mod download

# ✅ Copy Source Code
COPY . ./

# ✅ Build the Service
RUN go build -o series-service

# ✅ Expose the Port
EXPOSE 8082

# ✅ Start the Server
CMD ["./series-service"]
