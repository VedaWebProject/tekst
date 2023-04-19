FROM node:18.15-alpine AS builder

ARG WEB_PATH
ARG SERVER_URL
ARG API_PATH

ENV TEKST_SERVER_URL=$SERVER_URL \
    TEKST_API_PATH=$API_PATH

WORKDIR "/app"
COPY . .
RUN npm install && npm run build-only -- --base=$WEB_PATH


FROM caddy:2.6-alpine AS prod

WORKDIR "/var/www/html"
COPY --from=builder /app/dist/ ./
COPY ./deploy/Caddyfile /etc/caddy/
# 82:82 is alpine default for www-data
RUN set -x && adduser -u 82 -D -S -G www-data www-data
USER www-data
EXPOSE 80
