#!/bin/bash
# https://medium.com/@codingmaths/bin-bash-what-exactly-is-this-95fc8db817bf

{ read -d'\n' DB_USERNAME DB_PASSWORD DB_HOST DB_PORT DB_NAME DB_SCHEMA; } < <(aws secretsmanager get-secret-value --secret-id realestate-db-creds --region ap-southeast-2 --output json | jq -r '.SecretString' | jq -r '.username, .password, .host, .port, .dbname, .dbschema')
export DB_USERNAME DB_PASSWORD DB_HOST DB_PORT DB_NAME DB_SCHEMA

echo $DB_USERNAME
echo $DB_PASSWORD
echo $DB_HOST
echo $DB_PORT
echo $DB_NAME
echo $DB_SCHEMA