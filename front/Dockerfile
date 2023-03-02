FROM node:12

ADD . /app
WORKDIR /app
RUN yarn install
RUN yarn build

FROM nginx
COPY --from=0 /app/dist /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf