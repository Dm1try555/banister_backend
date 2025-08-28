import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

class GoogleCalendarService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        try:
            service_account_file = os.path.join(settings.BASE_DIR, 'google-credentials.json')
            
            if not os.path.exists(service_account_file):
                print("Google credentials file not found at google-credentials.json")
                return
            
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            self.service = build('calendar', 'v3', credentials=self.credentials)
            print("Google Calendar initialized successfully")
            
        except Exception as e:
            print(f"Google Calendar API initialization error: {str(e)}")
    
    def create_event(self, booking, calendar_id='primary'):
        if not self.service:
            return False, "Google Calendar API not initialized"
        
        try:
            event_data = {
                'summary': f'Meeting: {booking.service.title}',
                'description': f'Service: {booking.service.title}\nCustomer: {booking.customer.email}\nService Provider: {booking.provider.email}',
                'start': {
                    'dateTime': booking.scheduled_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (booking.scheduled_datetime + timedelta(hours=1)).isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': booking.customer.email},
                    {'email': booking.provider.email}
                ],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meet_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                }
            }
            
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()
            
            return True, event.get('id')
            
        except Exception as e:
            return False, f"Event creation error: {str(e)}"
    
    def create_interview_event(self, interview=None, user=None, scheduled_datetime=None, calendar_id='primary'):
        if not self.service:
            return False, "Google Calendar API not initialized"
        
        try:
            if interview:
                event_data = {
                    'summary': f'Interview: {interview.service.title if interview.service else "Service Interview"}',
                    'description': f'Interview for service\nProvider: {interview.provider.email}',
                    'start': {'dateTime': scheduled_datetime.isoformat(), 'timeZone': 'UTC'},
                    'end': {'dateTime': (scheduled_datetime + timedelta(hours=1)).isoformat(), 'timeZone': 'UTC'},
                    'attendees': [{'email': interview.provider.email}],
                    'conferenceData': {
                        'createRequest': {
                            'requestId': f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                        }
                    }
                }
            else:
                event_data = {
                    'summary': f'Test Interview: {user.email}',
                    'description': f'Test interview invitation\nUser: {user.email}',
                    'start': {'dateTime': scheduled_datetime.isoformat(), 'timeZone': 'UTC'},
                    'end': {'dateTime': (scheduled_datetime + timedelta(hours=1)).isoformat(), 'timeZone': 'UTC'},
                    'attendees': [{'email': user.email}],
                    'conferenceData': {
                        'createRequest': {
                            'requestId': f"test_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                        }
                    }
                }
            
            event = self.service.events().insert(
                calendarId=calendar_id, body=event_data, conferenceDataVersion=1, sendUpdates='all'
            ).execute()
            
            # Extract Google Meet link
            meet_link = None
            if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
                for entry_point in event['conferenceData']['entryPoints']:
                    if entry_point.get('entryPointType') == 'video':
                        meet_link = entry_point.get('uri')
                        break
            
            return True, {
                'event_id': event.get('id'),
                'meet_link': meet_link
            }
            
        except Exception as e:
            return False, f"Interview event creation error: {str(e)}"

google_calendar_service = GoogleCalendarService()