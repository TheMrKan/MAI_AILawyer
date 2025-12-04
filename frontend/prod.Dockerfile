FROM alpine:3.18
WORKDIR /app

COPY ./dist ./dist
CMD ["tail", "-f", "/dev/null"]