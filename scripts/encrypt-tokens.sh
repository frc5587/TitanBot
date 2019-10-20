#!/bin/sh

# Encrypts tokens stored in the tokens/ directory to upload them Github. This script uses the
# $TOKEN_DECRYPT_PASS environment variable (set by Heroku in our case) as the passphrase during encryption

# Get the path that the tokens are stored in
token_dir="./tokens"

# --batch to prevent interactive command --yes to assume "yes" for questions
if [ "$1" = "discord" ] || [ "$1" = "all" ]; then
    echo "Encrypting Discord token..."
    gpg --quiet --batch --yes --passphrase "$TOKEN_DECRYPT_PASS" --symmetric \
        --cipher-algo AES256 "$token_dir/discord-token.txt"
fi

if [ "$1" = "calendar" ] || [ "$1" = "all" ]; then
    echo "Encrypting Google Calendar credentials..."
    gpg --quiet --batch --yes --passphrase "$TOKEN_DECRYPT_PASS" --symmetric \
        --cipher-algo AES256 "$token_dir/calendar-credentials.json"
fi

if [ "$1" = "gtoken" ] || [ "$1" = "all" ]; then
    echo "Encrypting Google token..."
    gpg --quiet --batch --yes --passphrase "$TOKEN_DECRYPT_PASS" --symmetric \
        --cipher-algo AES256 "$token_dir/calendar-token.pickle"
fi

echo "Finished"
