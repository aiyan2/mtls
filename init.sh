#!/bin/bash

# Define base directory for certificates
BASE_DIR=./certs/mutual-tls
CA_DIR=$BASE_DIR/ca
SERVER_DIR=$BASE_DIR/server
CLIENT_DIR=$BASE_DIR/client

# Create directories if they don't exist
mkdir -p $CA_DIR $SERVER_DIR $CLIENT_DIR

# CA Certificate Generation
echo "### Generating CA Certificate ###"
openssl genpkey -algorithm RSA -out $CA_DIR/ca.key -aes256
openssl req -new -x509 -days 3650 -key $CA_DIR/ca.key -out $CA_DIR/ca.crt -subj "/CN=MyDevCA"

# Server Certificate Generation
echo "### Generating Server Certificate ###"
openssl genpkey -algorithm RSA -out $SERVER_DIR/server.key
openssl req -new -key $SERVER_DIR/server.key -out $SERVER_DIR/server.csr -subj "/CN=localhost"
openssl x509 -req -in $SERVER_DIR/server.csr -CA $CA_DIR/ca.crt -CAkey $CA_DIR/ca.key -CAcreateserial -out $SERVER_DIR/server.crt -days 3650

# Client Certificate Generation
echo "### Generating Client Certificate ###"
openssl genpkey -algorithm RSA -out $CLIENT_DIR/client.key
openssl req -new -key $CLIENT_DIR/client.key -out $CLIENT_DIR/client.csr -subj "/CN=client"
openssl x509 -req -in $CLIENT_DIR/client.csr -CA $CA_DIR/ca.crt -CAkey $CA_DIR/ca.key -CAcreateserial -out $CLIENT_DIR/client.crt -days 3650

# Completion
echo "Certificates have been generated successfully!"
echo " - CA Certificate: $CA_DIR/ca.crt"
echo " - CA Private Key: $CA_DIR/ca.key"
echo " - Server Certificate: $SERVER_DIR/server.crt"
echo " - Server Private Key: $SERVER_DIR/server.key"
echo " - Client Certificate: $CLIENT_DIR/client.crt"
echo " - Client Private Key: $CLIENT_DIR/client.key"
