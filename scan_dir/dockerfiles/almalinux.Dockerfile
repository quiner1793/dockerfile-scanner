FROM almalinux:8
RUN apk add --update nginx
CMD ["nginx", "-g", "daemon off;"]
