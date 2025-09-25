#!/bin/bash

# Set SSL certificate path for macOS
export SSL_CERT_FILE=$(python3 -m certifi)
export REQUESTS_CA_BUNDLE=$(python3 -m certifi)

# Alternative SSL paths for macOS (fallback)
if [ -z "$SSL_CERT_FILE" ]; then
    export SSL_CERT_FILE="/etc/ssl/cert.pem"
    export REQUESTS_CA_BUNDLE="/etc/ssl/cert.pem"
fi

# Run the agent
python3 main.py dev