from django.contrib import admin
from .models import PaymentByStudent, SubscriptionForStudent, SubscriptionPlanForDormitory, DormitorySubscription
from dateutil.relativedelta import relativedelta


class PaymentByStudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'method', 'status', 'paid_at')
    list_filter = ('status', 'method')
    search_fields = ('student__username',)
    ordering = ('-paid_at',)
    readonly_fields = ('paid_at', )


class SubscriptionForStudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'start_date', 'end_date', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('student__user__username', 'created_by')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Agar obuna mavjud bo'lsa
            fieldsets += (
                ('Subscription Status', {
                    'fields': ('is_active', 'start_date', 'end_date')
                }),
            )
        return fieldsets


class SubscriptionPlanForDormitoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_months', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('-created_at', 'created_by')


class DormitorySubscriptionAdmin(admin.ModelAdmin):
    list_display = ('dormitory', 'plan', 'start_date', 'end_date', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'plan')
    search_fields = ('dormitory__name', 'plan__name')
    ordering = ('-created_at', 'created_by')
    readonly_fields = ('created_at', 'created_by')

    def save_model(self, request, obj, form, change):
        # Avtomatik end_date ni hisoblash
        if not obj.end_date and obj.plan:
            obj.end_date = obj.start_date + relativedelta(months=obj.plan.duration_months)
        super().save_model(request, obj, form, change)


admin.site.register(PaymentByStudent, PaymentByStudentAdmin)
admin.site.register(SubscriptionForStudent, SubscriptionForStudentAdmin)
admin.site.register(SubscriptionPlanForDormitory, SubscriptionPlanForDormitoryAdmin)
admin.site.register(DormitorySubscription, DormitorySubscriptionAdmin)
