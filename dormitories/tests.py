from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import timedelta

from accounts.models import User
from universities.models import University
from dormitories.models import Dormitory, Floor, Room, DormitoryImage, RoomImage


class DormitoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='adminuser', password='pass1234', email='sardorbek@gmail.com')
        self.university = University.objects.create(name='Test University')

    def test_create_dormitory(self):
        dormitory = Dormitory.objects.create(
            name='Alpha Dormitory',
            university=self.university,
            address='123 Main St',
            city='Andijan',
            number_of_floors=5,
            subscription_end_date=timezone.now().date() + timedelta(days=365),
            admin=self.user,
            status='active'
        )
        self.assertEqual(str(dormitory), f"{dormitory.name} ({dormitory.city}) - {self.university.name}")

    def test_dormitory_ordering(self):
        Dormitory.objects.create(name='B Dormitory', university=self.university, address='...', city='...', number_of_floors=1, subscription_end_date=timezone.now().date())
        Dormitory.objects.create(name='A Dormitory', university=self.university, address='...', city='...', number_of_floors=1, subscription_end_date=timezone.now().date())
        dorms = Dormitory.objects.all()
        self.assertEqual(dorms.first().name, 'A Dormitory')


class FloorModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='adminuser', password='pass1234', email='sardorbek@gmail.com')
        self.university = University.objects.create(name='Test University')
        self.dormitory = Dormitory.objects.create(
            name='Test Dormitory',
            university=self.university,
            address='Address',
            city='City',
            number_of_floors=5,
            subscription_end_date=timezone.now().date(),
            admin=self.user,
        )

    def test_create_floor(self):
        floor = Floor.objects.create(
            dormitory=self.dormitory,
            floor_number=2,
            rooms_number=10,
            gender_type='female'
        )
        self.assertEqual(str(floor), f"Floor {floor.floor_number} - {self.dormitory.name}")

    def test_unique_floor_number(self):
        Floor.objects.create(dormitory=self.dormitory, floor_number=1, rooms_number=5)
        with self.assertRaises(IntegrityError):
            Floor.objects.create(dormitory=self.dormitory, floor_number=1, rooms_number=6)


class RoomModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='adminuser', password='pass1234', email='sardorbek@gmail.com')
        self.university = University.objects.create(name='Test University')
        self.dormitory = Dormitory.objects.create(
            name='Test Dormitory',
            university=self.university,
            address='Address',
            city='City',
            number_of_floors=3,
            subscription_end_date=timezone.now().date(),
            admin=self.user,
        )
        self.floor = Floor.objects.create(dormitory=self.dormitory, floor_number=1, rooms_number=5)

    def test_create_room(self):
        room = Room.objects.create(
            dormitory=self.dormitory,
            floor=self.floor,
            room_number='101A',
            capacity=4,
            current_occupancy=2,
        )
        self.assertEqual(str(room), f"Floor {self.floor.floor_number} - Room {room.room_number}")
        self.assertFalse(room.is_full)

    def test_room_full_property(self):
        room = Room.objects.create(
            dormitory=self.dormitory,
            floor=self.floor,
            room_number='102B',
            capacity=2,
            current_occupancy=2,
        )
        self.assertTrue(room.is_full)

    def test_occupancy_cannot_exceed_capacity(self):
        with self.assertRaises(ValueError):
            Room.objects.create(
                dormitory=self.dormitory,
                floor=self.floor,
                room_number='103C',
                capacity=3,
                current_occupancy=5,
            )

    def test_unique_room_number_on_same_floor(self):
        Room.objects.create(floor=self.floor, dormitory=self.dormitory, room_number='104D', capacity=2)
        with self.assertRaises(IntegrityError):
            Room.objects.create(floor=self.floor, dormitory=self.dormitory, room_number='104D', capacity=3)


class DormitoryImageTest(TestCase):
    def setUp(self):
        self.university = University.objects.create(name='Test University')
        self.user = User.objects.create_user(username='admin', password='pass1234', email='sardorbek@gmail.com')
        self.dormitory = Dormitory.objects.create(
            name='Test Dorm',
            university=self.university,
            address='Addr',
            city='City',
            number_of_floors=2,
            subscription_end_date=timezone.now().date(),
            admin=self.user,
        )

    def test_dormitory_image_upload(self):
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        dorm_img = DormitoryImage.objects.create(dormitory=self.dormitory, image=image)
        self.assertIn(self.dormitory.name, str(dorm_img))


class RoomImageTest(TestCase):
    def setUp(self):
        self.university = University.objects.create(name='Test University')
        self.user = User.objects.create_user(username='admin', password='pass1234', email='sardorbek@gmail.com')
        self.dormitory = Dormitory.objects.create(
            name='Test Dorm',
            university=self.university,
            address='Addr',
            city='City',
            number_of_floors=2,
            subscription_end_date=timezone.now().date(),
            admin=self.user,
        )
        self.floor = Floor.objects.create(dormitory=self.dormitory, floor_number=1, rooms_number=2)
        self.room = Room.objects.create(dormitory=self.dormitory, floor=self.floor, room_number='105', capacity=3)

    def test_room_image_upload(self):
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        room_img = RoomImage.objects.create(room=self.room, image=image)
        self.assertIn(str(self.room), str(room_img))
