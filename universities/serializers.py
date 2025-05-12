from rest_framework import serializers
from .models import University, Faculty


class FacultySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name']



class UniversitySerializer(serializers.ModelSerializer):
    faculties = FacultySimpleSerializer(many=True, read_only=True)

    class Meta:
        model = University
        fields = [
            'id',
            'name',
            'city',
            'address',
            'description',
            'contact_info',
            'website',
            'logo',
            'created_at',
            'updated_at',
            'faculties',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'city': {'required': True, 'allow_blank': False},
            'description': {'allow_null': True, 'required': False},
            'contact_info': {'allow_null': True, 'required': False},
            'website': {'allow_null': True, 'required': False},
            'logo': {'allow_null': True, 'required': False},
        }

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Universitet nomi kamida 3 ta belgidan iborat bo‘lishi kerak.")
        return value

    def validate_city(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Shahar nomi kamida 2 ta belgidan iborat bo‘lishi kerak.")
        return value


class FacultySerializer(serializers.ModelSerializer):
    university_name = serializers.StringRelatedField(source='university', read_only=True)

    class Meta:
        model = Faculty
        fields = [
            'id',
            'university',  # bu PrimaryKey sifatida ishlatiladi
            'university_name',  # bu faqat o‘qish uchun
            'name',
        ]
        read_only_fields = ['id', 'university_name']
        extra_kwargs = {
            'university': {'required': True},
            'name': {'required': True, 'allow_blank': False},
        }

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Fakultet nomi kamida 3 ta belgidan iborat bo‘lishi kerak.")
        return value

    def validate(self, attrs):
        university = attrs.get('university')
        name = attrs.get('name')

        if Faculty.objects.filter(university=university, name__iexact=name).exists():
            raise serializers.ValidationError("Bu universitetda bunday nomli fakultet allaqachon mavjud.")
        return attrs
