from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Public
    path("movies/", views.MovieListView.as_view(), name="movies"),
    path("movies/<int:id>/shows/", views.ShowListByMovieView.as_view(), name="movie-shows"),

    # Booking (auth required)
    path("shows/<int:id>/book/", views.BookShowView.as_view(), name="book-show"),
    path("my-bookings/", views.MyBookingsView.as_view(), name="my-bookings"),
    path("bookings/<int:booking_id>/cancel/", views.CancelBookingView.as_view(), name="cancel-booking"),
]
