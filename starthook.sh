#!/bin/sh
echo -e 'GET /set_webhook HTTP/1.0\r\n\r\n' | openssl s_client -connect 188.130.155.45:8443
