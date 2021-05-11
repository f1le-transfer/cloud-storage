FROM node:14.16.1-alpine 
RUN mkdir -p /app/node_modules && chown -R node:node /app/
WORKDIR /app
COPY package*.json .
USER node
RUN npm install
COPY --chown=node:node . .
EXPOSE 5050
CMD [ "npm", "start" ]
