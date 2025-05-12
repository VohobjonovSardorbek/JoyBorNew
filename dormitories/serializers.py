from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Dormitory, Floor, Room, DormitoryImage, RoomImage
from universities.models import University
from django.contrib.auth import get_user_model

User = get_user_model()


class UniversityShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'address', 'city']


class DormitoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DormitoryImage
        fields = ['id', 'image']


class DormitorySerializer(serializers.ModelSerializer):
    university = UniversityShortSerializer(read_only=True)
    admin = UserSerializer(read_only=True)
    images = DormitoryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Dormitory
        fields = ['id', 'name', 'university', 'address', 'city', 'number_of_floors', 'description', 'created_at',
                  'admin', 'subscription_end_date', 'status', 'contact_info', 'latitude', 'longitude', 'updated_at',
                  'images']


class DormitoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dormitory
        fields = ['name', 'university', 'address', 'city', 'number_of_floors', 'description', 'subscription_end_date',
                  'status', 'contact_info', 'latitude', 'longitude']


class FloorSerializer(serializers.ModelSerializer):
    dormitory = DormitorySerializer(read_only=True)
    rooms = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Floor
        fields = ['id', 'dormitory', 'floor_number', 'rooms_number', 'description', 'gender_type', 'created_at',
                  'updated_at', 'rooms']


class FloorCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ['dormitory', 'floor_number', 'rooms_number', 'description', 'gender_type']


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['id', 'image']


class RoomSerializer(serializers.ModelSerializer):
    dormitory = DormitorySerializer(read_only=True)
    floor = FloorSerializer(read_only=True)
    images = RoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'dormitory', 'floor', 'room_number', 'capacity', 'current_occupancy', 'status', 'description',
                  'created_at',
                  'updated_at', 'is_full', 'images']


class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['dormitory', 'floor', 'room_number', 'capacity', 'current_occupancy', 'status', 'description']

    def validate(self, data):
        if data['current_occupancy'] > data['capacity']:
            raise serializers.ValidationError("Current occupancy cannot exceed room capacity.")
        return data
