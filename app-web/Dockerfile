FROM node:lts-alpine3.18

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE ${FRONTEND_METRO_PORT} ${FRONTEND_EXPO_DEVTOOLS_PORT}

CMD ["npm", "run", "web"]
