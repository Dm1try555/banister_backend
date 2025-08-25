class SwaggerMixin:
    """
    Миксин для корректной работы Swagger при генерации схемы
    """
    def get_queryset(self):
        # Если это Swagger генерация схемы - возвращаем пустой queryset
        if getattr(self, 'swagger_fake_view', False):
            # Определяем модель из queryset или из класса
            if hasattr(self, 'queryset') and self.queryset is not None:
                return self.queryset.model.objects.none()
            elif hasattr(self, 'model'):
                return self.model.objects.none()
            else:
                # Fallback - возвращаем пустой queryset
                from django.db.models.query import QuerySet
                return QuerySet().none()
        
        # Иначе вызываем родительский метод
        return super().get_queryset()
    
    def get_object(self):
        # Если это Swagger генерация схемы - возвращаем None
        if getattr(self, 'swagger_fake_view', False):
            return None
        
        # Иначе вызываем родительский метод
        return super().get_object() 