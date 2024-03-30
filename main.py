import os.path
from argparse import ArgumentParser
from copy import deepcopy
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/contacts"]


def main(force: bool, limit: Optional[int]):
    print(f'Including {limit if limit else "all"} people')
    print(f'Will {"UPDATE" if force else "NOT UPDATE"} contacts')
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

        connections = get_connections(service, limit)

        for person in connections:
            names = person.get("names", [])
            name = names[0].get("displayName") if names else 'NONAME'
            print(f'{person["resourceName"]} - {name}')
            numbers = person.get('phoneNumbers', [])
            original_numbers = deepcopy(numbers)
            changed = False
            for number in numbers:
                if number['value'].startswith('8'):
                    value = number["value"]
                    fixed_value = fix_number(value)
                    print(f'  {number.get("type", "NOTYPE")} - {value} -> {fixed_value}')
                    number['value'] = fixed_value
                    changed = True
            if changed:
                print('  Before')
                print(f"    {original_numbers}")
                print('  After')
                print(f"    {numbers}")
            if force:
                service.people().updateContact(
                    resourceName=person['resourceName'],
                    body=person,
                    personFields="names,phoneNumbers",
                    updatePersonFields="phoneNumbers"
                ).execute()
    except HttpError as err:
        print(err)


def get_connections(service, limit: Optional[int]):
    results = service.people() \
        .connections() \
        .list(resourceName="people/me", pageSize=1000, personFields="names,phoneNumbers") \
        .execute()
    connections = [
        connection
        for connection
        in results.get("connections", [])
        if connection.get('phoneNumbers', []) and any(
            number['value'].startswith('8') for number in connection.get('phoneNumbers'))
    ]
    return connections[:limit]


def fix_number(original: str) -> str:
    fixed = original
    if fixed.startswith('8'):
        fixed = '+370' + fixed[1:]
    return fixed


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-f', '--force', default=False, action='store_true')
    parser.add_argument('-l', '--limit', action='store', type=int)
    args = parser.parse_args()
    main(args.force, args.limit)
