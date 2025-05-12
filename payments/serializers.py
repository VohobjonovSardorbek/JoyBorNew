from rest_framework import serializers
from .models import *
from students.models import Student
from datetime import date


class PaymentByStudentReadSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source='get_method_display', read_only=True, max_length=255)
    status_display = serializers.CharField(source='get_status_display', read_only=True, max_length=255)
    student_username = serializers.CharField(source='student.username', read_only=True, max_length=255)

    class Meta:
        model = PaymentByStudent
        fields = [
            'id',
            'student',
            'student_username',
            'amount',
            'method',
            'method_display',
            'status',
            'status_display',
            'paid_at',
            'receipt',
        ]
        read_only_fields = fields  # Barchasi faqat ko‘rsatish uchun


class PaymentByStudentWriteSerializer(serializers.ModelSerializer):
    method = serializers.ChoiceField(choices=PaymentMethod.choices)
    status = serializers.ChoiceField(choices=PaymentStatus.choices)

    class Meta:
        model = PaymentByStudent
        fields = [
            'amount',
            'method',
            'status',
            'receipt',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['student'] = request.user
        return super().create(validated_data)


class PaymentShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentByStudent
        fields = ['id', 'amount', 'method', 'status']


class DormitoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dormitory
        fields = ['id', 'name', 'university']


class SubscriptionForStudentSerializer(serializers.ModelSerializer):
    student_user_username = serializers.CharField(source='student.user.username', read_only=True, max_length=255)
    payment_info = PaymentShortSerializer(source='payment', read_only=True)
    dormitory_info = DormitoryShortSerializer(source='dormitory', read_only=True)
    days_left = serializers.IntegerField(read_only=True)
    created_by = serializers.CharField(source='created_by.username',
                                       read_only=True)  # created_by username ni ko‘rsatadi

    class Meta:
        model = SubscriptionForStudent
        fields = [
            'id',
            'student',
            'student_user_username',
            'dormitory',
            'dormitory_info',
            'payment',
            'payment_info',
            'start_date',
            'end_date',
            'is_active',
            'days_left',
            'created_at',
            'created_by',  # yangi qo‘shilgan maydon
        ]
        read_only_fields = ['student', 'payment_info', 'days_left', 'created_at', 'created_by']

    def validate(self, attrs):
        payment = attrs.get('payment')
        student = attrs.get('student')

        if payment and student and payment.student != student.user:
            raise serializers.ValidationError("To‘lov talaba foydalanuvchisiga mos kelmaydi.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Foydalanuvchi faqat superadmin yoki yotoqxona admin bo‘lishi kerak
            if request.user.is_superuser or request.user.is_super_admin or request.user.is_dormitory_admin:
                validated_data['created_by'] = request.user  # created_by ni belgilaymiz
            else:
                raise serializers.ValidationError("Faqat admin yoki yotoqxona admini obuna yaratishi mumkin.")
        return super().create(validated_data)


class SubscriptionPlanForDormitorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlanForDormitory
        fields = [
            'id',
            'name',
            'description',
            'price',
            'duration_months',
            'is_active',
            'payment_proof',
            'created_at',
            'created_by',  # created_by ham qo'shildi
        ]
        read_only_fields = ['created_at', 'created_by']

    def create(self, validated_data):
        # Foydalanuvchi kontekstini olish
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        # Foydalanuvchi autentifikatsiya qilingan bo'lsa va admin bo'lsa
        if user and (user.is_superuser or user.is_dormitory_admin):
            validated_data['created_by'] = user  # created_by maydonini foydalanuvchi bilan yangilash
        else:
            raise serializers.ValidationError("Faqat admin yoki yotoqxona admini obuna yaratishi mumkin.")

        # Create va ma'lumotlarni saqlash
        return super().create(validated_data)


class DormitorySubscriptionSerializer(serializers.ModelSerializer):
    dormitory_name = serializers.CharField(source='dormitory.name', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_price = serializers.DecimalField(source='plan.price', read_only=True, decimal_places=2, max_digits=20)
    plan_duration = serializers.IntegerField(source='plan.duration_months', read_only=True)
    days_left = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = DormitorySubscription
        fields = [
            'id',
            'dormitory',
            'dormitory_name',
            'plan',
            'plan_name',
            'plan_price',
            'plan_duration',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
            'created_by_username',
            'days_left',
        ]
        read_only_fields = [
            'created_at',
            'dormitory_name',
            'plan_name',
            'plan_price',
            'plan_duration',
            'days_left',
            'created_by_username'
        ]

    def get_days_left(self, obj):
        if obj.end_date and obj.is_active:
            return (obj.end_date - date.today()).days
        return 0

    def create(self, validated_data):
        request = self.context.get('request')
        dormitory = validated_data.get('dormitory')
        plan = validated_data.get('plan')

        if not dormitory or not plan:
            raise serializers.ValidationError("Both 'dormitory' and 'plan' fields are required.")

        subscription = DormitorySubscription.objects.create(
            dormitory=dormitory,
            plan=plan,
            start_date=validated_data.get('start_date', date.today()),
            is_active=validated_data.get('is_active', True),
            created_by=request.user
        )

        # End date calculation
        subscription.end_date = subscription.start_date + relativedelta(months=plan.duration_months)
        subscription.save()
        return subscription

    def update(self, instance, validated_data):
        plan = validated_data.get('plan', instance.plan)

        # Update plan or start date triggers new end_date
        if 'plan' in validated_data or 'start_date' in validated_data:
            start_date = validated_data.get('start_date', instance.start_date)
            instance.end_date = start_date + relativedelta(months=plan.duration_months)

        return super().update(instance, validated_data)
