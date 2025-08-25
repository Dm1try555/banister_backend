class SwaggerMixin:
    """
    Mixin for correct Swagger operation when generating schema
    """
    def get_queryset(self):
        # If this is Swagger generation - return empty queryset
        if getattr(self, 'swagger_fake_view', False):
            # Define model from queryset or from class
            if hasattr(self, 'queryset') and self.queryset is not None:
                return self.queryset.model.objects.none()
            elif hasattr(self, 'model'):
                return self.model.objects.none()
            else:
                # Fallback - return empty queryset
                from django.db.models.query import QuerySet
                return QuerySet().none()
        
        # Otherwise call parent method
        return super().get_queryset()
    
    def get_object(self):
        # If this is Swagger generation - return None
        if getattr(self, 'swagger_fake_view', False):
            return None
        
        # Otherwise call parent method
        return super().get_object() 