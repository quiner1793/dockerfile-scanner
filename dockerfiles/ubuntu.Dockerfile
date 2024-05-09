FROM ubuntu:18.04
RUN apk add --update nginx
CMD ["nginx", "-g", "daemon off;"]
