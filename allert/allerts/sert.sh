#/bit/sh

openssl genrsa -out key.pem 2048

openssl req -new -x509 -key key.pem -out cert-365days.pem -days 365 -subj "/CN=localhost"

#openssl req -new -x509 -key key.pem -out cert-7days.pem -days 7 -subj "/CN=localhost"

#docker-compose up --build