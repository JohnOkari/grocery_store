## Grocery Store API (Django + DRF)

This project provides a simple API for categories, products, and orders, with email/SMS notifications.

### Features
- Django 5 + Django REST Framework
- Category tree via django-mptt
- Product create + bulk upload
- Order creation that triggers email/SMS notifications
- Tests with pytest + coverage (threshold enforced)

## 1) Prerequisites
- Python 3.12
- PostgreSQL 13+ (or run Postgres via Docker)

## 2) Create a virtualenv and install dependencies
```bash
python -m venv venv
# Linux/macOS (bash)
source venv/bin/activate
# Windows PowerShell
# .\\venv\\Scripts\\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Configure environment variables
- If present, copy the template and edit values:
```bash
cp .env.example .env
```
- If the template is not present, create `.env` and add required values (see variables listed in `.env.example` section below).

Important variables:
- `POSTGRES_*` for the database
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- Email and Africa's Talking settings (only needed if you want real sends)

The app automatically loads `.env` on startup.

## 4) Start PostgreSQL (Docker example)
```bash
docker run --name grocery-postgres \
  -e POSTGRES_DB=grocery_store \
  -e POSTGRES_USER=developer \
  -e POSTGRES_PASSWORD=root \
  -p 5432:5432 -d postgres:16
```
If you use different values, update `.env` accordingly.

## 5) Apply migrations and create an admin user
```bash
python manage.py migrate
python manage.py createsuperuser
```

## 6) Run the server
```bash
python manage.py runserver
```
Open `http://127.0.0.1:8000/`

### Authentication
Default permission is `IsAuthenticated`.
- SessionAuthentication: log into `/admin/` and use the browsable API
- BasicAuthentication: send basic auth headers

### API endpoints (prefixed with `/api/`)
- POST `/api/categories/` — create a category
- POST `/api/products/` — create a product
- POST `/api/products/bulk/` — bulk create (JSON list or CSV under `file`)
- GET  `/api/average-price/<int:category_id>/` — average price including descendants
- POST `/api/orders/` — create an order (sends notifications)

Example: Create a category
```bash
curl -u myuser:mypass -X POST http://127.0.0.1:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Fruits", "parent": null}'
```

Example: Bulk upload products (JSON)
```bash
curl -u myuser:mypass -X POST http://127.0.0.1:8000/api/products/bulk/ \
  -H "Content-Type: application/json" \
  -d '{"products": [{"name": "Apple", "price": 10, "category_name": "Fruits"}]}'
```

## 7) Run tests and view coverage
```bash
pytest --cov=store --cov-report=term-missing
# or generate HTML
pytest --cov=store --cov-report=html
```
Coverage threshold is enforced in `setup.cfg`.

## 8) Notifications in development
- Email: default backend prints emails to console. Tests use locmem backend.
- SMS: Africa's Talking is a no-op unless `AFRICASTALKING_API_KEY` is set. Tests stub the network call.

## 9) Troubleshooting
- If `ALLOWED_HOSTS` error: set `ALLOWED_HOSTS=127.0.0.1,localhost` in `.env`
- PowerShell activation: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- Port 5432 busy: change Docker port mapping or stop the conflicting service

## 10) Project layout
- `grocery_store/` — project settings and URLs
- `store/` — app (models, serializers, views, tests)
- `.env.example` — environment template
- `pytest.ini`, `setup.cfg` — test and coverage config


