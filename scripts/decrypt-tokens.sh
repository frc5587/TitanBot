#!/bin/sh

# Decrypts the encrypted tokens stored in the tokens/ directory based on
# the $TOKEN_DECRYPT_PASS environment variable (set by Heroku in our case)

# Get the path that the tokens are stored in
token_dir="./tokens"

# --batch to prevent interactive command --yes to assume "yes" for questions
if [ "$1" == "discord" ]; then
    gpg --quiet --batch --yes --decrypt --passphrase "$TOKEN_DECRYPT_PASS" \
        --output "$token_dir/discord-token.txt" "$token_dir/discord-token.txt.gpg"
elif [ "$1" == "calendar" ]; then
    gpg --quiet --batch --yes --decrypt --passphrase "$TOKEN_DECRYPT_PASS" \
        --output "$token_dir/calendar-credentials.json" "$token_dir/calendar-credentials.json.gpg"
elif [ "$1" == "gtoken" ]; then
    gpg --quiet --batch --yes --decrypt --passphrase "$TOKEN_DECRYPT_PASS" \
        --output "$token_dir/calendar-token.pickle" "$token_dir/calendar-token.pickle.gpg"
fi
