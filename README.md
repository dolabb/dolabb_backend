# Dolabb Backend API

A comprehensive Django REST API backend for Dolabb, a modern marketplace
platform supporting multi-user roles (Admin, Buyers, Sellers, Affiliates) with
real-time chat, payment processing, and affiliate management.

## 🚀 Features

### Core Functionality

- **Multi-Role Authentication**: Admin, Buyer, Seller, and Affiliate user types
  with JWT-based authentication
- **OTP Verification**: Email-based OTP verification using Resend API
- **Admin Dashboard**: Comprehensive admin panel with analytics, user
  management, and system monitoring
- **Product Management**: Full CRUD operations for listings with approval
  workflow
- **Real-Time Chat**: WebSocket-based messaging system for buyer-seller
  communication
- **Payment Processing**: Integration with Moyasar payment gateway
- **Affiliate System**: Complete affiliate management with commission tracking
- **Notification System**: Real-time notifications via WebSocket
- **Dispute Management**: Admin tools for handling buyer-seller disputes
- **Cashout Requests**: Seller payout request management

### Technical Features

- **MongoDB Database**: NoSQL database using MongoEngine ODM
- **RESTful API**: Clean REST API architecture
- **WebSocket Support**: Real-time communication using Django Channels
- **File Storage**: Support for local and VPS-based file storage
- **CORS Enabled**: Cross-origin resource sharing configured
- **JWT Authentication**: Secure token-based authentication
- **Pagination**: Built-in pagination for list endpoints

## 🛠️ Tech Stack

- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: MongoDB (via MongoEngine 0.27.0)
- **Authentication**: JWT (PyJWT 2.8.0)
- **Real-Time**: Django Channels 4.0.0 with Redis
- **Email**: Resend API
- **Payment**: Moyasar Gateway
- **Server**: Gunicorn + Daphne (ASGI)

## 📋 Prerequisites

- Python 3.8+
- MongoDB (local or MongoDB Atlas)
- Redis (for WebSocket support)
- Resend API account (for email OTP)
- Moyasar account (for payments)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Setup Script (Optional)

```bash
python setup.py
```

This will create a `.env` file template and check Redis connection.

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## 🚀 Running the Application

### Development Server

```bash
# Run Django development server
python manage.py runserver

# Run with ASGI (for WebSocket support)
daphne -b 0.0.0.0 -p 8000 dolabb_backend.asgi:application
```

### Production Server

```bash
# Using Gunicorn (HTTP)
gunicorn dolabb_backend.wsgi:application --bind 0.0.0.0:8000

# Using Daphne (ASGI - includes WebSocket)
daphne -b 0.0.0.0 -p 8000 dolabb_backend.asgi:application
```

## 🏗️ Project Structure

```
backend/
├── admin_dashboard/      # Admin panel APIs
├── affiliates/           # Affiliate management
├── authentication/       # Auth & user management
├── chat/                 # Real-time chat system
├── notifications/        # Notification system
├── payments/             # Payment processing
├── products/             # Product/listing management
├── dolabb_backend/       # Django project settings
├── storage/              # File storage utilities
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔐 Authentication

All endpoints (except authentication endpoints) require JWT token in the
Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### User Types

1. **Admin**: Full system access
2. **User/Buyer**: Can browse, purchase, and chat
3. **Seller**: Can create listings and manage orders
4. **Affiliate**: Can earn commissions from referrals

## 📦 Key Modules

### Authentication Module

- User signup/login with OTP verification
- Password reset functionality
- JWT token generation and validation
- Multi-role support

### Admin Dashboard Module

- Dashboard statistics and analytics
- User management (suspend, deactivate, reactivate)
- Listing approval workflow
- Transaction monitoring
- Dispute resolution
- Cashout request management
- Fee settings configuration

### Products Module

- Product CRUD operations
- Category management
- Offer system
- Review and rating system
- Search and filtering

### Chat Module

- Real-time messaging via WebSocket
- File upload support
- Conversation management
- Online user status

### Payments Module

- Moyasar payment integration
- Transaction tracking
- Order management

### Affiliates Module

- Affiliate registration
- Commission tracking
- Payout requests
- Earnings breakdown

## 🧪 Testing

```bash
# Run tests (if available)
python manage.py test
```

## 🚢 Deployment

### Render.com

The project includes `render.yaml` for easy deployment on Render.com.

### Environment Variables

Ensure all environment variables are set in your deployment platform:

- MongoDB connection string
- Resend API key
- JWT secret key
- Moyasar credentials
- Redis connection details

### Production Settings

Use `settings_production.py` for production deployment with appropriate security
configurations.

## 📝 API Documentation

For detailed API documentation, refer to the Postman collection:

- `Dolabb_Backend_API.postman_collection.json`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 👥 Support

For support, email support@dolabb.com or open an issue in the repository.

## 🔄 Version

**Current Version**: 1.2.0

---

**Built with ❤️ for Dolabb Marketplace**
