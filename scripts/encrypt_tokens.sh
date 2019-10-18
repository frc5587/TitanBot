#!/bin/sh

# Encrypts tokens stored in the tokens/ directory to upload them Github. This script uses the
# $TOKEN_DECRYPT_PASS environment variable (set by Heroku in our case) as the passphrase during encryption

# Get the path that the tokens are stored in
token_dir="./tokens/"

# --batch to prevent interactive command --yes to assume "yes" for questions
gpg --quiet --batch --yes --passphrase "$TOKEN_DECRYPT_PASS" --symmetric \
    --cipher-algo AES256 "$token_dir/discord-token.txt"
gpg --quiet --batch --yes --passphrase "$TOKEN_DECRYPT_PASS" --symmetric \
    --cipher-algo AES256 "$token_dir/calendar-credentials.json"
