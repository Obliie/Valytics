FROM node:lts-alpine3.18

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 19006

CMD ["npm", "run", "web"]
