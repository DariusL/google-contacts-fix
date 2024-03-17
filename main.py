import os.path
from argparse import ArgumentParser
from copy import deepcopy

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/contacts"]


def main(force: bool):
    token = None
    if os.path.exists("token.json"):
        token = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not token or not token.valid:
        if token and token.expired and token.refresh_token:
            token.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            token = flow.run_local_server(port=0)
        with open("token.json", "w") as token_file:
            token_file.write(token.to_json())

    try:
        service = build("people", "v1", credentials=token)

        connections = get_connections(service)

        for person in connections:
            names = person.get("names", [])
            name = names[0].get("displayName") if names else 'NONAME'
            print(f'{person["resourceName"]} - {name}')
            numbers = deepcopy(person.get('phoneNumbers', []))
            for number in numbers:
                if number['value'].startswith('8'):
                    value = number["value"]
                    print(f'  {number.get("type", "NOTYPE")} - {value} -> {fix_number(value)}')
    except HttpError as err:
        print(err)


def get_connections(service):
    results = service.people() \
        .connections() \
        .list(resourceName="people/me", pageSize=100, personFields="names,phoneNumbers") \
        .execute()
    connections = [
        connection
        for connection
        in results.get("connections", [])
        if connection.get('phoneNumbers', []) and any(
            number['value'].startswith('8') for number in connection.get('phoneNumbers'))
    ]
    return connections


def fix_number(original: str) -> str:
    fixed = original
    if fixed.startswith('8'):
        fixed = '+370' + fixed[1:]
    return fixed


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-f', '--force', default=False, action='store_true')
    args = parser.parse_args()
    print(args.force)
    main(args.force)
