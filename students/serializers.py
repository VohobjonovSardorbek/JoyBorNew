from rest_framework import serializers
from accounts.models import User
from .models import Student, Application, APPLICATION_STATUS
from dormitories.models import Dormitory
from universities.models import University, Faculty


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        write_only=True,
        source='user'
    )
    university = serializers.PrimaryKeyRelatedField(queryset=University.objects.all(), allow_null=True, required=False)
    faculty = serializers.PrimaryKeyRelatedField(
        queryset=Faculty.objects.none(),  # dynamic filtering
        allow_null=True,
        required=False
    )

    class Meta:
        model = Student
        fields = [
            'id',
            'user',
            'user_id',
            'passport_number',
            'father_name',
            'university',
            'faculty',
            'additional_phone',
            'emergency_contact_name',
            'emergency_contact_phone',
            'discount',
            'social_status',
            'payment_proof',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        university_id = self.context.get('university_id')
        if university_id:
            self.fields['faculty'].queryset = Faculty.objects.filter(university_id=university_id)

    def validate_passport_number(self, value):
        if len(value) != 9:
            raise serializers.ValidationError("Passport number must be exactly 9 characters long.")
        return value

    def validate_payment_proof(self, value):
        if value and value.size > 5 * 1024 * 1024:  # 5MB dan katta bo‘lsa
            raise serializers.ValidationError("File size must be less than 5MB.")
        return value

    def create(self, validated_data):
        return Student.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = validated_data.pop('user', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if user:
            instance.user = user
        instance.save()
        return instance


class ApplicationSerializer(serializers.ModelSerializer):
    student = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Auto-fill with current user
    dormitory = serializers.PrimaryKeyRelatedField(queryset=Dormitory.objects.all())
    status = serializers.ChoiceField(choices=APPLICATION_STATUS, default='pending')
    student_document = serializers.FileField(required=False)
    submitted_at = serializers.DateTimeField(read_only=True)
    reviewed_at = serializers.DateTimeField(required=False, allow_null=True)
    comment = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'student',
            'dormitory',
            'student_document',
            'status',
            'submitted_at',
            'reviewed_at',
            'comment'
        ]
        read_only_fields = ['submitted_at']

    def validate_student_document(self, value):
        """Validatsiya studentning hujjati uchun."""
        if value and value.size > 5 * 1024 * 1024:  # 5MB dan katta bo‘lsa
            raise serializers.ValidationError("Document size must be less than 5MB.")
        return value

    def validate(self, attrs):
        """Kombinatsion validatsiya: dormitory va student."""
        dormitory = attrs.get('dormitory')
        student = attrs.get('student')

        if Application.objects.filter(dormitory=dormitory, student=student, status='pending').exists():
            raise serializers.ValidationError("This student already has a pending application for this dormitory.")

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
