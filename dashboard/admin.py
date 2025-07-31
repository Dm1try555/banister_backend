from django.contrib import admin
from .models import DashboardStats

@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_bookings', 'total_earnings']
    list_filter = ['user__role']
    search_fields = ['user__email']
