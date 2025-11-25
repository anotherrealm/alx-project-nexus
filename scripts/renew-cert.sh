#!/bin/bash

docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot renew --quiet --deploy-hook \"\
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec nginx nginx -s reload\"" certbot
