FROM node:lts-alpine AS frontbuilder
ADD front /app
WORKDIR /app
RUN yarn install
ENV NODE_OPTIONS=--openssl-legacy-provider
RUN yarn build --target app

FROM python:3.11
LABEL maintainer="zensec@zenika.com"

ENV DEBUG=1
ADD zenscanner zenscanner
WORKDIR /zenscanner
RUN useradd -m zenscanner -u 1000
RUN chmod +x start.sh start-worker.sh
RUN chown -R zenscanner:zenscanner /zenscanner/
RUN pip install pipenv -r requirements.txt
USER zenscanner

COPY --from=frontbuilder /app/dist /zenscanner/app


