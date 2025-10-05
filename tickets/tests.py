from django.urls import reverse
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from tickets.models import Movie, Show, Booking

class BookingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.m1 = Movie.objects.create(title="Interstellar", duration_minutes=169)
        now = timezone.now()
        self.s1 = Show.objects.create(movie=self.m1, screen_name="Screen 1", date_time=now + timedelta(hours=2), total_seats=5)

    def auth(self):
        res = self.client.post(reverse("token_obtain_pair"), {"username":"alice","password":"password123"}, format="json")
        self.assertEqual(res.status_code, 200)
        token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_01_signup_and_login(self):
        res = self.client.post(reverse("signup"), {"username": "bob", "password": "passw0rd"}, format="json")
        self.assertEqual(res.status_code, 201)
        res = self.client.post(reverse("token_obtain_pair"), {"username":"bob","password":"passw0rd"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)

    def test_02_movies_and_shows_public(self):
        res = self.client.get(reverse("movies"))
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)
        res = self.client.get(reverse("movie-shows", args=[self.m1.id]))
        self.assertEqual(res.status_code, 200)

    def test_03_booking_and_double_booking(self):
        self.auth()
        res = self.client.post(reverse("book-seat", args=[self.s1.id]), {"seat_number": 1}, format="json")
        self.assertEqual(res.status_code, 201)
        # double booking same seat should fail
        self.auth()
        res = self.client.post(reverse("book-seat", args=[self.s1.id]), {"seat_number": 1}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_04_invalid_seat_numbers(self):
        self.auth()
        res = self.client.post(reverse("book-seat", args=[self.s1.id]), {"seat_number": 0}, format="json")
        self.assertEqual(res.status_code, 400)
        res = self.client.post(reverse("book-seat", args=[self.s1.id]), {"seat_number": 999}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_05_auth_required(self):
        res = self.client.post(reverse("book-seat", args=[self.s1.id]), {"seat_number": 2}, format="json")
        self.assertEqual(res.status_code, 401)

    def test_06_user_cannot_cancel_others_booking(self):
        self.auth()
        res = self.client.post(reverse("book-seat", args=[self.s1.id]), {"seat_number": 3}, format="json")
        self.assertEqual(res.status_code, 201)
        booking_id = res.data["id"]

        # new user tries to cancel
        self.client.credentials()
        User.objects.create_user(username="mallory", password="passw0rd")
        res2 = self.client.post(reverse("token_obtain_pair"), {"username":"mallory","password":"passw0rd"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res2.data['access']}")
        res3 = self.client.post(reverse("cancel-booking", args=[booking_id]))
        self.assertEqual(res3.status_code, 403)
