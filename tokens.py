import os.path
import pickle
import subprocess
import sys
from typing import List
from google_auth_oauthlib.flow import InstalledAppFlow


def read_discord_token() -> str:
    """
    Fetches the client secret for the Discord bot.
    If the decrypted text file containing the token cannot be found and the user
    is on a POSIX system, an attempt is made to decrypt the encrypted copy of the
    token included in this repository using gpg (see README for details).

    :raises RuntimeError: Raised when reading the Discord token was unsuccessful
    :return: discord token
    :rtype: str
    """

    unencrypted_file = "./tokens/discord-token.txt"
    encrypted_file = "./tokens/discord-token.txt.gpg"

    # If decrypted discord token doesn't exist, try to decrypt token with gpg
    if should_attempt_decrypt(unencrypted_file):
        print("Unable to find Discord token; trying to decrypt token...")
        attempt_decrypt(encrypted_file, "discord")

    # Check that decrypted tokens exist now
    if os.path.exists(unencrypted_file):
        with open(unencrypted_file, "r") as file:
            lines = file.readlines()
            return lines[0].strip()

    # No token files (encrypted or otherwise) or on Windows and can't decrypt, so throw error
    raise RuntimeError("Could not fetch Discord bot token")


def read_calendar_credentials(scopes: List[str]) -> InstalledAppFlow:
    """
    Fetches the InstalledAppFlow for the Google Calendar credentials.
    If the decrypted JSON file containing the credentials cannot be found and the user
    is on a POSIX system, an attempt is made to decrypt the encrypted copy of the JSON
    credentials included in this repository using gpg (see README for details).

    :param scopes: Scopes of the Google Calendar credentials for creating the Flow
    :type scopes: List[str]
    :raises RuntimeError: Raised when reading the credentials was unsuccessful
    :return: Object to get Google data
    :rtype: InstalledAppFlow
    """

    unencrypted_file = "./tokens/calendar-credentials.json"
    encrypted_file = "./tokens/calendar-credentials.json.gpg"

    # If decrypted discord token doesn't exist, try to decrypt token with gpg
    if should_attempt_decrypt(unencrypted_file):
        print(
            "Unable to find Google Calendar credentials; trying to decrypt credentials..."
        )
        attempt_decrypt(encrypted_file, "calendar")

    # Check that decrypted tokens exist now and return it
    if os.path.exists(unencrypted_file):
        return InstalledAppFlow.from_client_secrets_file(
            'tokens/calendar-credentials.json', scopes)

    # No token files (encrypted or otherwise) or on Windows and can't decrypt, so throw error
    raise RuntimeError("Could not fetch Google Calendar credentials")


def read_google_token() -> pickle:
    """
    Fetches the Google token from a previously generated pickle.
    This token is created and stored to prevent the bot from having to go through
    the full authorisation process for Google Calendar each time it is run, as the
    process cannot be completed on services such as Heroku.
    If the decrypted pickle containing the token cannot be found and the user
    is on a POSIX system, an attempt is made to decrypt the encrypted copy of the
    token included in this repository using gpg (see README for details).

    :raises RuntimeError: Raised when reading the credentials was unsuccessful
    :return: Google token previously generated through Flow
    :rtype: Object
    """
    unencrypted_file = "./tokens/calendar-token.pickle"
    encrypted_file = "./tokens/calendar-token.pickle.gpg"

    # If decrypted discord token doesn't exist, try to decrypt token with gpg
    if should_attempt_decrypt(unencrypted_file):
        print("Unable to find cached Google token; trying to decrypt token...")
        attempt_decrypt(encrypted_file, "gtoken")

    # Check that decrypted tokens exist now and return it
    if os.path.exists(unencrypted_file):
        with open('tokens/calendar-token.pickle', 'rb') as token:
            return pickle.load(token)

    # No token files (encrypted or otherwise) or on Windows and can't decrypt, so throw error
    raise RuntimeError("Could not fetch Google Calendar credentials")


def should_attempt_decrypt(unencrypted_file: str) -> bool:
    """
    Determine whether an attempt to decrypt a token should be
    made, or if the token can be read now.

    :param unencrypted_file: the path that should lead to the unencrypted file
    :type unencrypted_file: str
    :return: whether to attempt decryption
    :rtype: bool
    """
    return not os.path.exists(unencrypted_file) and sys.platform in [
        "posix", "darwin", "linux"
    ]


def attempt_decrypt(encrypted_file: str, decrypt_type: str) -> None:
    """
    Attempts to decrypt the encrypted file provided by passing the decrypt type provided
    into `decrypt-tokens.sh`. The method checks that encrypted_file exists and then passes decrypt_
    type to the `./scripts/decrypt-tokens` script if it does. Valid values for `decrypt_type` are
    "discord", "calendar", and "gtoken".

    :param encrypted_file: the path of the file to decrypt
    :type encrypted_file: str
    :param decrypt_type: decryption type option to pass to bash script.
    :type decrypt_type: str
    :raises FileNotFoundError: Raised when encrypted_file is not a valid path
    :raises EnvironmentError: Raised when bash script errors and exits
    """

    # Look for encrypted token
    if not os.path.exists(encrypted_file):
        raise FileNotFoundError(f"Unable to find encrypted discord token `{encrypted_file}`")

    # Run decrypt script
    decrypt_command = ["bash ./scripts/decrypt-tokens.sh", decrypt_type]
    return_code = subprocess.call(decrypt_command)

    # Check that it was successful
    if return_code == 1:
        raise EnvironmentError(
            f"Unable to decrypt `{encrypted_file}`, even though it exists." +
            "Is TOKEN_DECRYPT_PASS an environment variable?")
