FROM python:3-slim
WORKDIR /app
VOLUME ["/test"]
COPY . .
EXPOSE 5050
CMD [ "python", "./block-server/server.py" ]
