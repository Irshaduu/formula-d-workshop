# Formula D – Workshop Management System

> A personal survival and learning tool for premium car workshop operations

**Formula D** is a single-user Django web application designed to help workshop technicians work faster, avoid mistakes, and build confidence in daily operations. It's not a commercial product—it's a practical tool built for real workshop life.

---

## 🎯 Purpose

This app helps you:
- ✅ Record job cards **faster than paper**
- ✅ Reduce spelling errors with **smart autocomplete**
- ✅ Learn car brands, models, and spare parts **over time**
- ✅ Build a **personal knowledge base** for repairs and solutions
- ✅ Work efficiently on **mobile devices** inside the workshop

---

## 🧠 Core Philosophy

```
Simple > Smart
Clear > Clever
Calm > Complex
```

The app should feel like writing on paper, but faster and cleaner. No feature should slow you down or force strict rules.

---

## 🏗️ System Architecture

### Two Logical Layers

#### 1. **Study Layer** (Reference Only)
- Car Brands & Models
- Spare Parts
- Common Concerns & Solutions
- Used **only for autocomplete suggestions**
- Never blocks manual typing

#### 2. **Job Card Layer** (Daily Work)
- Stores everything as **text fields**
- Manual typing is **always allowed**
- Autocomplete is only a helper
- Old job cards **never break** if study data changes

---

## 💻 Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11 | Backend language |
| **Django** | 5.2.9 | Web framework |
| **SQLite** | Default | Database (single-user) |
| **Bootstrap** | 5.3.0 | UI framework |
| **HTML/CSS/JS** | Vanilla | Frontend (no frameworks) |

### What's NOT Included
- ❌ No REST APIs
- ❌ No React/Vue/Angular
- ❌ No authentication (single-user only)
- ❌ No invoicing, GST, or PDF generation
- ❌ No auto-calculations
- ❌ No admin panel dependency for daily use

---

## 📋 Features

### 🏠 Home - Job Card Entry
- Quick vehicle detail entry (Registration, Brand, Model, Mileage)
- Customer information (Name, Contact)
- Dynamic customer concerns section
- Swipeable spare parts table (mobile-optimized)
- Swipeable labour/jobs table (mobile-optimized)
- Autocomplete for brands, models, and spare parts

### 📜 Jobs - Job Card List
- View all saved job cards (newest first)
- Edit existing job cards
- Delete job cards with confirmation
- Search and filter capabilities

### 📚 Study - Knowledge Base
- **Cars & Models:** Brand logos in a grid, drill down to models
- **Spare Parts:** Simple list of common part names
- **Concerns & Solutions:** Knowledge base for repair patterns
- Add, edit items to improve autocomplete suggestions

### 🎨 Design Features
- **Mobile-first** responsive design
- **Dark mode** support (automatic based on system preference)
- **Eye-comfortable** color scheme (light and dark)
- **Big touch targets** for easy mobile interaction
- **Labels above inputs** for clarity
- **Clean spacing** and calm colors

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. **Clone or download** this repository:
   ```bash
   cd formulad_workshop
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser** (optional, for admin panel):
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Open your browser:**
   ```
   http://127.0.0.1:8000
   ```

### For Local Development
If you want detailed error messages during development, edit `settings.py`:
```python
DEBUG = True  # Only for local testing
```
Remember to set it back to `False` before deployment!

---

## 📱 Usage Guide

### First-Time Setup

1. **Populate Study Data** (recommended before creating job cards):
   - Navigate to **Study → Cars & Models**
   - Add common car brands you work with
   - Add models for each brand
   - Navigate to **Study → Spare Parts**
   - Add common spare part names
   - Navigate to **Study → Concerns & Solutions**
   - Add typical customer concerns and their solutions

2. **Create Your First Job Card**:
   - Click **Home** in the navbar
   - Fill in vehicle details (Registration, Brand, Model are most important)
   - Add customer concerns (click "+ Add Concern" for more)
   - Add spare parts used (click "+ Add Spare" to add rows)
   - Add labour/jobs performed (click "+ Add Job" to add rows)
   - Click **Save Job Card**

3. **Review Jobs**:
   - Click **Jobs** in the navbar to see all saved job cards
   - Click **Edit** to modify any job card
   - Click **Delete** to remove a job card (with confirmation)

### Mobile Usage Tips
- **Swipe left/right** on Spare Parts and Jobs tables to see all columns
- Use the **numeric keyboard** for mileage and prices
- **Autocomplete** appears as you type in brand, model, and spare part fields
- **Registration numbers** automatically convert to UPPERCASE

---

## 📁 Project Structure

```
formulad_workshop/
├── formulad_workshop/      # Project settings
│   ├── settings.py         # Django configuration
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI entry point
├── workshop/              # Main application
│   ├── migrations/        # Database migrations
│   ├── templates/         # HTML templates
│   │   └── workshop/
│   │       ├── base.html           # Base template
│   │       ├── jobcard/            # Job card templates
│   │       └── study/              # Study section templates
│   ├── admin.py           # Admin panel configuration
│   ├── forms.py           # Form definitions
│   ├── models.py          # Database models
│   ├── urls.py            # App URL patterns
│   └── views.py           # View logic
├── static/                # Static files (CSS, JS)
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── script.js      # Custom JavaScript
├── media/                 # Uploaded files (brand logos, etc.)
├── db.sqlite3            # SQLite database
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 🗄️ Database Models

### Study Section Models
- **CarBrand**: Car manufacturer names and logos
- **CarModel**: Car models linked to brands
- **SparePart**: Common spare part names
- **ConcernSolution**: Knowledge base of problems and fixes

### Job Card Models
- **JobCard**: Main job card with vehicle and customer details
- **JobCardConcern**: Customer concerns for each job
- **JobCardSpareItem**: Spare parts used (with quantity, price, total)
- **JobCardLabourItem**: Labour/jobs performed (with amounts)

---

## 🔧 Admin Panel (Optional)

Access the Django admin at `http://127.0.0.1:8000/admin/`

**Features:**
- Manage all study data (brands, models, spares, concerns)
- View and edit job cards with inline formsets
- Search and filter capabilities
- Bulk actions

**Note:** You don't need the admin panel for daily workshop use—it's there if you want it.

---

## 🌐 Deployment to PythonAnywhere

### Pre-Deployment Checklist
- [ ] Ensure `DEBUG = False` in `settings.py` ✅ (already done)
- [ ] Update `ALLOWED_HOSTS` with your domain:
  ```python
  ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
  ```
- [ ] Set a strong `SECRET_KEY` using environment variables
- [ ] Run `python manage.py collectstatic` to gather static files
- [ ] Test all features locally before deploying

### Deployment Steps
1. Create a PythonAnywhere account
2. Upload your code or clone from Git
3. Set up a virtual environment
4. Install requirements: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Configure WSGI file to point to your project
7. Set up static files mapping in PythonAnywhere web tab
8. Reload your web app

Full deployment guide: [PythonAnywhere Django Tutorial](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)

---

## 🎨 Customization

### Change Color Scheme
Edit CSS variables in `workshop/templates/workshop/base.html` (lines 23-50):
```css
:root {
    --color-bg: #f0f2f5;        /* Background color */
    --color-card: #fafbfc;      /* Card background */
    --color-text: #2c3e50;      /* Text color */
    --color-primary: #0d6efd;   /* Primary color */
    /* ... more variables ... */
}
```

### Add New Fields to Job Card
1. Add field to `JobCard` model in `models.py`
2. Create and run migration: `python manage.py makemigrations && python manage.py migrate`
3. Add field to `JobCardForm` in `forms.py`
4. Update template: `workshop/templates/workshop/jobcard/jobcard_form.html`

---

## 🐛 Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Database Issues
Reset the database (⚠️ deletes all data):
```bash
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Migration Conflicts
```bash
python manage.py migrate --run-syncdb
```

### Server Won't Start
Check for syntax errors:
```bash
python manage.py check
```

---

## 📝 License

This is a personal project. Use it however you want. No warranties, no support guarantees—just a tool to make workshop life easier.

---

## 🤝 Contributing

This is a personal single-user system, but if you find it useful and want to adapt it for your own workshop, feel free to fork and modify!

---

## 📧 Contact

Built with ❤️ for real workshop survival, not for impressing developers.

---

**Remember:** If something feels confusing, it's wrong. The app should help you work faster, not slower. Keep it simple, keep it calm. 🚗💨
