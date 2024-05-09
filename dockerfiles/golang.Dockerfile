# Use the official Go base image
FROM golang:1.21-alpine as build

# Set the working directory in the container
WORKDIR /app

# Copy the application code
COPY /src .

# Build application using static compilation
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags="-s -w -extldflags \"-static\"" -o go_app

# Set the working directory in the container
WORKDIR /

# Run the application as a non-root user
RUN addgroup -g 1000 myuser \
    && adduser -D -u 1000 -G myuser myuser
VOLUME "/data"
USER myuser

# Expose port 8070
EXPOSE 8070

# Run application
CMD [ "./go_app" ]