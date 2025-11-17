# Dolabb Backend

Django REST Framework backend for Dolabb marketplace platform.

## Features

- ✅ User Authentication (Admin, Buyers, Sellers, Affiliates)
- ✅ Product Management (CRUD, Search, Filter)
- ✅ Real-time Chat System (WebSockets)
- ✅ Offer Management
- ✅ Payment Processing (Moyasar)
- ✅ Admin Dashboard
- ✅ Affiliate Program
- ✅ Notification System (Real-time)
- ✅ MongoDB Database

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Update MongoDB connection string
   - Add Resend API key
   - Add Moyasar API keys

3. **Run Redis** (for WebSockets):
   ```bash
   redis-server
   ```

4. **Run server:**
   ```bash
   python manage.py runserver
   # Or for WebSockets:
   daphne dolabb_backend.asgi:application
   ```

## Documentation

See [SETUP_DOCUMENTATION.md](./SETUP_DOCUMENTATION.md) for detailed setup instructions including:
- WebSockets configuration
- Moyasar payment gateway setup
- API documentation
- Troubleshooting guide

## Project Structure

```
dolabb_backend/
├── authentication/      # User authentication
├── admin_dashboard/      # Admin panel APIs
├── products/            # Product management
├── chat/                # Chat system (WebSockets)
├── payments/            # Payment processing
├── affiliates/          # Affiliate program
└── notifications/       # Notification system
```

## API Base URL

```
http://localhost:8000/api/
```

## License

Proprietary

