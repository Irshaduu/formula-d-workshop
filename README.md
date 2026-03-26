# WorkshopOS - Workshop Management System

A premium, comprehensive Django-based workshop management system designed to streamline automotive service operations. Manage job cards, inventory, customer vehicles, and invoicing all in one professional platform.

## Features

### Role-Based Access Control (RBAC)
- **Multi-Tenant Permissions** - Dedicated access levels for **Owner**, **Office**, and **Floor (Mechanic)** roles.
- **Secure Admin Hub** - OTP-protected login for Owners and restricted management views.
- **Role-specific UI** - Dynamic navigation and information visibility based on user groups.

### Job Card Management
- **Digital Job Cards** - Create and manage service records with customer details, vehicle information, and work performed.
- **Real-time Status Tracking** - Progress bars and visual status cues on the "Live Report" dashboard.
- **Auto-Learning Database** - System automatically captures new concerns and spare parts for future smart-suggestions (Case-insensitive & Whitespace Normalized).
- **Safety Hardened** - Double-confirmation modals for renames and deletes, and Dynamic Merge Alerts to protect historical data.

### Inventory System
- **Stock Management** - Track parts and consumables with low-stock alerts and percentage-based color coding.
- **Consumption Tracking** - Automatically record part usage from job cards.
- **Category Organization** - Group inventory items for easier management and restocking.

### Dashboard & Layout
- **Live Report Dashboard** - High-visibility "Floor" view for mechanics and "Live Report" for office staff.
- **Mobile Optimized** - Premium responsive design with a native-app feel and bottom navigation on mobile.
- **Skeleton Loading** - Professional shimmer animations for a smooth, high-performance user experience.

### Invoice & Billing
- **Professional Invoices** - Auto-generated, itemized invoices with company branding.
- **Cost Analytics** - Automatic calculations for parts, labour, and tax.
- **Sequential Billing** - Standardized billing numbers (e.g., WOS-26-001).

## Tech Stack

- **Backend**: Python 3.13 / Django 5.2.12 LTS
- **Database**: SQLite (personal backup enabled) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, Vanilla JavaScript, CSS3
- **Security**: python-decouple for environment variables, role-based decorators, OTP Auth.

## Installation

### Prerequisites
- Python 3.13+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Irshaduu/formula-d-workshop.git
   cd formula-d-workshop
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Rename `.env.example` to `.env`
   - Set your `SECRET_KEY`, `DEBUG`, and `TIME_ZONE="Asia/Kolkata"`.

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
WorkshopOS/
├── workshop/               # Core application (Job cards, Auth, Management)
├── inventory/              # Inventory & Stock management app
├── formulad_workshop/      # Project configuration & settings
├── static/                 # Global assets & collected static files
├── media/                  # User uploaded vehicle images/profiles
├── requirements.txt        # Python dependencies
└── manage.py               # Django management script
```

## Maintenance & Optimization
- **Database Optimization** - Aggregate queries used to prevent N+1 performance bottlenecks.
- **Log Rotation** - Automatic error log rotation (5MB limit, 5-file history).
- **Security** - Custom decorators protect sensitive administrative routes.

---

**Version**: 3.0  
**Last Updated**: March 2026  
**Status**: Production Ready
