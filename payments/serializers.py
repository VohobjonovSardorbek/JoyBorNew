from rest_framework import serializers
from .models import *


class MonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = ['id', 'name']


class StudentShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'name',
            'last_name'
        ]


class PaymentForStudentReadSerializer(serializers.ModelSerializer):
    student = StudentShortSerializer(read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True, max_length=255)
    month = serializers.PrimaryKeyRelatedField(queryset=Month.objects.all(), many=True)

    class Meta:
        model = PaymentForStudent
        fields = [
            'id',
            'student',
            'amount',
            'method',
            'description',
            'method_display',
            'created_at',
            'month',
        ]
        read_only_fields = fields  # Barchasi faqat ko‘rsatish uchun


class PaymentForStudentWriteSerializer(serializers.ModelSerializer):
    method = serializers.ChoiceField(choices=PaymentMethod.choices)
    month = MonthSerializer(many=True)

    class Meta:
        model = PaymentForStudent
        fields = [
            'student',
            'amount',
            'method',
            'description',
            'month',
        ]


