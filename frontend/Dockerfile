FROM node:lts

WORKDIR /app

COPY package.json /app/package.json

RUN npm install

COPY . /app

CMD ["npm", "start"]