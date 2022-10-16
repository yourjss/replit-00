FROM nginx:alpine
# FROM python:3.6-alpine

WORKDIR /pyty

COPY main.py .
COPY lib.zip .

RUN apk update && \
    apk add --no-cache ca-certificates && \
    chmod +x main.py
    
RUN apk add --update --no-cache python3

EXPOSE 8800

CMD ["python3", "main.py"]
