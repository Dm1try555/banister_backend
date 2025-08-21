from apps.authentication.models import User
from core.google_calendar.service import google_calendar_service

class InterviewMixin:
    def notify_admins(self, instance, provider_email):
        for admin in User.objects.filter(is_staff=True):
            self.create_notification(
                user=admin,
                notification_type='NewInterviewRequest',
                data={'interview_id': instance.id},
                push_title='New Interview Request',
                push_body='Provider wants interview'
            )
    
    def handle_calendar(self, interview, data):
        if data.get('status') == 'scheduled' and data.get('scheduled_datetime'):
            success, event_id = google_calendar_service.create_interview_event(interview, data['scheduled_datetime'])
            if success:
                data['google_calendar_event_id'] = event_id
        return data
    
    def send_status_notification(self, interview):
        if interview.status == 'scheduled':
            self.create_notification(
                user=interview.customer,
                notification_type='InterviewScheduled',
                data={'interview_id': interview.id, 'status': interview.status},
                push_title='Interview Scheduled',
                push_body='Your interview has been scheduled'
            )
        elif interview.status == 'rejected':
            self.create_notification(
                user=interview.customer,
                notification_type='InterviewRejected',
                data={'interview_id': interview.id, 'status': interview.status},
                push_title='Interview Rejected',
                push_body='Your interview request was rejected'
            )
        elif interview.status == 'completed':
            self.create_notification(
                user=interview.customer,
                notification_type='InterviewCompleted',
                data={'interview_id': interview.id, 'status': interview.status},
                push_title='Interview Completed',
                push_body='Your interview has been completed'
            ) 