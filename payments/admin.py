from django.contrib import admin
from .models import PaymentForStudent


class PaymentByStudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'method', 'created_at')
    list_filter = ('method',)
    search_fields = ('student__name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


admin.site.register(PaymentForStudent, PaymentByStudentAdmin)
