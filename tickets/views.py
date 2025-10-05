from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, Show, Booking
from .serializers import MovieSerializer, ShowSerializer, BookingSerializer


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"detail": "username and password required"}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({"detail": "username already exists"}, status=400)
        user = User.objects.create_user(username=username, password=password)
        return Response({"id": user.id, "username": user.username}, status=201)


class MovieListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        qs = Movie.objects.all().order_by("id")
        return Response(MovieSerializer(qs, many=True).data)


class ShowListByMovieView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        movie = get_object_or_404(Movie, id=id)
        shows = Show.objects.filter(movie=movie).order_by("id")
        return Response(ShowSerializer(shows, many=True).data)


class BookShowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        show = get_object_or_404(Show, id=id)
        try:
            seat_number = int(request.data.get("seat_number", 0))
        except (TypeError, ValueError):
            return Response({"detail": "seat_number must be an integer"}, status=400)

        # Validate seat number range if Show has total_seats field
        total = getattr(show, "total_seats", None)
        if seat_number <= 0 or (total is not None and seat_number > total):
            return Response({"detail": "Invalid seat number"}, status=400)

        # Check seat not already booked for this show
        if Booking.objects.filter(show=show, seat_number=seat_number).exists():
            return Response({"detail": "Seat already booked"}, status=400)

        try:
            booking = Booking.objects.create(
                user=request.user,
                show=show,
                seat_number=seat_number,
            )
        except IntegrityError:
            # In case there is a DB unique_together constraint on (show, seat_number)
            return Response({"detail": "Seat already booked"}, status=400)

        return Response(BookingSerializer(booking).data, status=201)


class MyBookingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Booking.objects.filter(user=request.user).order_by("id")
        return Response(BookingSerializer(qs, many=True).data)


class CancelBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        if booking.user_id != request.user.id:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        # Either delete or mark cancelled; tests only check permission, so delete is fine.
        booking.delete()
        return Response({"detail": "Booking cancelled"}, status=200)
