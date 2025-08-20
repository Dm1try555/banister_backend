import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

class GoogleCalendarService:
    """Service for working with Google Calendar API"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar API"""
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
        """Create calendar event for booking"""
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

google_calendar_service = GoogleCalendarService()