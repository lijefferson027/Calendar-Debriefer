from __future__ import print_function

import datetime
import os.path
from twilio.rest import Client
import keys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main(calendar_ids):

    #set the variables
    today=datetime.date.today()
    start_of_day= datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0).isoformat()+'Z'
    end_of_day= datetime.datetime(today.year, today.month, today.day, 23, 59, 59, 999999).isoformat()+'Z'
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    SMS_message=''

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Iterate over the list of calendar IDs
        for calendar_id in calendar_ids:
            if calendar_id=='lisammi789@gmail.com':
                SMS_message+='Good Morning, Here is your events for the day:\n'
                events_result = service.events().list(calendarId=calendar_id, timeMin=start_of_day,
                                                  timeMax=end_of_day, maxResults=10, singleEvents=True,
                                                  orderBy='startTime').execute()
                events = events_result.get('items', [])
            
                if not events:
                    SMS_message+='No events for today, enjoy your day:)\n'
                else:
                # Print the events for the current calendar
                    for event in events:
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        summary=event['summary']
                        SMS_message+=f'{start} {summary}\n'

            else:
                SMS_message+='Here is your assignments that are due today:\n'
                events_result = service.events().list(calendarId=calendar_id, timeMin=start_of_day,
                                                  timeMax=end_of_day, maxResults=10, singleEvents=True,
                                                  orderBy='startTime').execute()
                events = events_result.get('items', [])
            
                if not events:
                    SMS_message+='No assignments for today, enjoy your day:)\n'
                else:
                # Print the events for the assignment calendar
                    for event in events:
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        summary=event['summary']
                        SMS_message+= f'{start} {summary}\n'

        client=Client(keys.account_sid, keys.authen_token)
        
        message=client.messages.create(
            body=SMS_message,
            from_=keys.twilio_number,
            to=keys.target_number
        )

        print(message.body)

    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    calendar_ids=['lisammi789@gmail.com', 'sekq5tfjbgvim7uo7k2cj2jn03l50c48@import.calendar.google.com']
    main(calendar_ids)