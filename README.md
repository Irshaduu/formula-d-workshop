# Formula D Workshop Management System

A comprehensive Django-based workshop management system designed to streamline automotive service operations. Manage job cards, inventory, customer vehicles, and invoicing all in one platform.

## Features

### Job Card Management
- **Digital Job Cards** - Create and manage service records with customer details, vehicle information, and work performed
- **Customer Concerns Tracking** - Document and track customer-reported issues with status updates (Pending/Working/Fixed)
- **Spare Parts Integration** - Add parts used with quantities, pricing, and availability status
- **Labour Tracking** - Record services performed with costs
- **Auto-Learning Database** - System automatically adds new concerns and spare parts to master data for future suggestions

### Dashboard & Workflow
- **Real-time Dashboard** - View all active vehicles in the workshop with progress tracking
- **Status Indicators** - Visual cues for on-hold jobs and delivery readiness
- **Delivery Management** - Mark jobs as delivered with automatic date stamping
- **Date Filtering** - Filter delivered vehicles by time period (today, week, month, year, custom range)
- **Role-based Access** - Different permissions for admin users and workshop staff

### Invoice Generation
- **Professional Invoices** - Auto-generated invoices with itemized breakdown
- **PDF Export** - Print-ready invoice format with company branding
- **Automatic Billing Numbers** - Sequential billing number generation (e.g., JB-26-001)
- **Cost Calculations** - Automatic totals for parts, labour, and overall costs

### Inventory & Master Data
- **Car Brands & Models** - Maintain database of vehicle makes and models
- **Spare Parts Library** - Master list of available parts with autocomplete
- **Concerns & Solutions** - Knowledge base of common issues and fixes
- **Smart Suggestions** - Brand-filtered model suggestions and concern/parts autocomplete

### User Experience
- **Dark/Light Theme** - Automatic theme switching based on system preferences
- **Mobile Responsive** - Works seamlessly on desktop, tablet, and mobile devices
- **Toast Notifications** - Non-intrusive success messages that auto-dismiss
- **Professional UI** - Clean, modern interface with intuitive navigation

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Authentication**: Django's built-in auth system
- **File Handling**: Django media files for images

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

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
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

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

8. **Access the application**
   - Open browser to `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## Usage

### For Workshop Staff
- Create job cards for incoming vehicles
- Update job status and add work performed
- Mark vehicles as delivered when ready

### For Administrators
- Access full dashboard with delivery controls
- Manage master data (brands, models, parts, concerns)
- Generate and view invoices
- Manage user accounts and permissions

## Project Structure

```
formulad_workshop/
├── workshop/               # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Django forms
│   ├── urls.py            # URL routing
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JS, images
│   └── migrations/        # Database migrations
├── formulad_workshop/     # Project settings
├── static/                # Collected static files
├── media/                 # User uploaded files
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Key Models

- **JobCard** - Service records with customer and vehicle details
- **JobCardConcern** - Customer-reported issues per job card
- **JobCardSpare** - Parts used in each job
- **JobCardLabour** - Services performed
- **CarBrand** / **CarModel** - Vehicle make/model database
- **SparePart** - Master parts inventory
- **ConcernSolution** - Knowledge base of common issues
- **CarProfile** - Vehicle history and profiles

## Configuration

Key settings in `.env`:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (set to False in production)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hostnames
- Database configuration (if using PostgreSQL)

## Contributing

This is a production workshop management system. For feature requests or bug reports, please contact the development team.

## License

Proprietary - All rights reserved

## Support

For technical support or feature requests, contact the system administrator.

---

**Version**: 2.0  
**Last Updated**: January 2026  
**Status**: Production
