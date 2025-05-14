from rest_framework import serializers
from accounts.models import User
from .models import Student, Application
from dormitories.models import Dormitory
from universities.models import University, Faculty


class StudentSerializer(serializers.ModelSerializer):
    faculty = serializers.PrimaryKeyRelatedField(
        queryset=Faculty.objects.none(),  # dynamic filtering
        allow_null=True,
        required=False
    )

    class Meta:
        model = Student
        fields = [
            'id',
            'name',
            'passport_number',
            'middle_name',
            'last_name',
            'dormitory',
            'faculty',
            'phone_number',
            'direction',
            'province',
            'district',
            'floor',
            'room',
            'emergency_contact_phone',
            'picture',
            'discount',
            'social_status',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dormitory = self.context.get('dormitory')
        if dormitory:
            self.fields['faculty'].queryset = Faculty.objects.filter(university=dormitory.university)

    def validate_passport_number(self, value):
        if len(value) != 9:
            raise serializers.ValidationError("Passport number must be exactly 9 characters long.")
        return value

    def create(self, validated_data):
        return Student.objects.create(**validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    student = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Auto-fill with current user
    dormitory = serializers.PrimaryKeyRelatedField(queryset=Dormitory.objects.all())
    submitted_at = serializers.DateTimeField(read_only=True)
    comment = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'student',
            'first_name',
            'last_name',
            'middle_name',
            'dormitory',
            'faculty',
            'province',
            'district',
            'passport_number',
            'phone_number',
            'comment',
            'picture',
            'submitted_at',
        ]
        read_only_fields = ['submitted_at']

    def validate(self, attrs):
        """Kombinatsion validatsiya: dormitory va student."""
        dormitory = attrs.get('dormitory')
        student = attrs.get('student')
        if Application.objects.filter(student=student, dormitory=dormitory).exists():
            raise serializers.ValidationError("Siz ushbu yotoqxonaga allaqachon ariza yuborgansiz.")
        return attrs

    def create(self, validated_data):
        """Create method to handle the creation of an application."""
        return Application.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update method to handle application updates."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
