# MovieBookingAPI (Recovered Build)

A minimal Django REST API for movie ticket booking with JWT auth and Swagger docs.

## Features
- Signup (`POST /signup/`)
- JWT token (`POST /api/token/`, `/api/token/refresh/`)
- List movies (`GET /movies/`)
- List shows for a movie (`GET /movies/{movie_id}/shows/`)
- Book a seat (`POST /shows/{id}/book/` with `{"seat_number": 1}`)
- My bookings (`GET /my-bookings/`)
- Cancel booking (`POST /bookings/{booking_id}/cancel/`)
- Swagger UI at `/swagger/`

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python manage.py migrate

# (optional) create superuser
# python manage.py createsuperuser

python manage.py runserver
# Open http://127.0.0.1:8000/swagger/
```



