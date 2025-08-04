import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from django.core.mail import send_mail
from authentication.models import User

class GoogleCalendarService:
    """Сервис для работы с Google Calendar API"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Инициализация Google Calendar API"""
        try:
            # Путь к файлу сервисного аккаунта
            service_account_file = os.path.join(settings.BASE_DIR, 'google-service-account.json')
            
            if not os.path.exists(service_account_file):
                print("Файл сервисного аккаунта Google не найден")
                return
            
            # Создание учетных данных
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            # Создание сервиса
            self.service = build('calendar', 'v3', credentials=self.credentials)
            
        except Exception as e:
            print(f"Ошибка инициализации Google Calendar API: {str(e)}")
    
    def create_meeting_event(self, booking, calendar_id='primary'):
        """Создание события встречи в Google Calendar"""
        if not self.service:
            return False, "Google Calendar API не инициализирован"
        
        try:
            # Формирование данных события
            event_data = self._prepare_event_data(booking)
            
            # Создание события
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data,
                sendUpdates='all'  # Отправка уведомлений всем участникам
            ).execute()
            
            return True, event.get('id')
            
        except Exception as e:
            return False, f"Ошибка создания события: {str(e)}"
    
    def _prepare_event_data(self, booking):
        """Подготовка данных события для Google Calendar"""
        # Время начала и окончания встречи (по умолчанию 1 час)
        start_time = booking.scheduled_datetime
        end_time = start_time + timedelta(hours=1)
        
        # Форматирование времени для Google Calendar
        start_time_str = start_time.isoformat()
        end_time_str = end_time.isoformat()
        
        # Описание встречи
        description = f"""
Сервис: {booking.service.title}
Клиент: {booking.customer.get_full_name() or booking.customer.email}
Провайдер: {booking.provider.get_full_name() or booking.provider.email}
Локация: {booking.location or 'Не указана'}
Примечания: {booking.notes or 'Нет'}
        """.strip()
        
        # Список участников
        attendees = []
        
        # Добавление клиента, если у него подтверждена почта
        if booking.customer.email and booking.customer.is_active:
            attendees.append({'email': booking.customer.email})
        
        # Добавление провайдера, если у него подтверждена почта
        if booking.provider.email and booking.provider.is_active:
            attendees.append({'email': booking.provider.email})
        
        event_data = {
            'summary': f'Встреча: {booking.service.title}',
            'description': description,
            'start': {
                'dateTime': start_time_str,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time_str,
                'timeZone': 'UTC',
            },
            'attendees': attendees,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # За день
                    {'method': 'popup', 'minutes': 30},       # За 30 минут
                ],
            },
        }
        
        return event_data
    
    def send_meeting_invitations(self, booking):
        """Отправка приглашений на встречу пользователям с подтвержденной почтой"""
        success_count = 0
        total_count = 0
        
        # Список пользователей для отправки приглашений
        users_to_notify = []
        
        # Добавление клиента
        if booking.customer.email and booking.customer.is_active:
            users_to_notify.append(booking.customer)
        
        # Добавление провайдера
        if booking.provider.email and booking.provider.is_active:
            users_to_notify.append(booking.provider)
        
        # Создание события в календаре
        calendar_success, calendar_result = self.create_meeting_event(booking)
        
        if calendar_success:
            success_count += 1
        
        # Отправка email уведомлений
        for user in users_to_notify:
            total_count += 1
            if self._send_meeting_email(user, booking):
                success_count += 1
        
        return {
            'calendar_created': calendar_success,
            'calendar_event_id': calendar_result if calendar_success else None,
            'emails_sent': success_count,
            'total_users': total_count
        }
    
    def _send_meeting_email(self, user, booking):
        """Отправка email уведомления о встрече"""
        try:
            subject = f'Приглашение на встречу: {booking.service.title}'
            
            message = f"""
Здравствуйте, {user.get_full_name() or user.email}!

Вас приглашают на встречу:

Сервис: {booking.service.title}
Дата и время: {booking.scheduled_datetime.strftime('%d.%m.%Y в %H:%M')}
Локация: {booking.location or 'Не указана'}
Клиент: {booking.customer.get_full_name() or booking.customer.email}
Провайдер: {booking.provider.get_full_name() or booking.provider.email}

Примечания: {booking.notes or 'Нет'}

С уважением,
Команда Banister
            """.strip()
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            print(f"Ошибка отправки email для {user.email}: {str(e)}")
            return False

# Глобальный экземпляр сервиса
google_calendar_service = GoogleCalendarService() 