# AgriGest

AgriGest is a premium Django-based agricultural management platform for farms and cooperatives. It centralizes parcel management, crop tracking, inventory, harvests, expenses, sales, and reporting in a single professional workspace.

## Project goals

- Professional agricultural SaaS experience
- Modular Django architecture
- Responsive and polished interface inspired by the Antigravity design direction
- Multi-farm isolation and authenticated access
- Real financial and operational tracking in FCFA and hectares

## Stack

- Backend: Python, Django, Django ORM, Django forms
- Frontend: Django templates, HTML5, CSS3, JavaScript, Chart.js
- Database: SQLite for local development
- Extras: reportlab, openpyxl

## Structure

```text
AgriGest/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── config/
│   ├── manage.py
│   ├── db.sqlite3
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/
│   │   ├── dashboard/
│   │   ├── parcelles/
│   │   ├── cultures/
│   │   ├── intrants/
│   │   ├── recoltes/
│   │   ├── depenses/
│   │   ├── ventes/
│   │   └── rapports/
│   ├── templates/
│   ├── static/
│   └── media/
├── env/
└── .venv/
```

## Quick start

1. Create or activate the project virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
copy .env.example .env
```

4. Apply migrations:

```bash
cd config
python manage.py migrate
```

5. Create a superuser (optional):

```bash
python manage.py createsuperuser
```

6. Seed demo data (recommended for a showcase):

```bash
python manage.py seed_demo_data
```

Default demo account:

- Username: ibrahim
- Password: AgriGest2026!

7. Start the development server:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Main modules

- Accounts and authentication
- Dashboard and KPIs
- Parcelle management
- Crop lifecycle tracking
- Stock and inputs management
- Harvest tracking
- Expense management
- Sales and customer tracking
- Reporting and analytics

## Security notes

- Secret keys and debug settings are environment-based.
- Authentication is managed through Django’s default auth system.
- Farm-level data separation is supported through `FarmProfile` and each model’s farm relationship.

## Demo data

The included `seed_demo_data` command populates a sample farm with realistic agricultural data for previewing the platform. It is clearly demo-only and should not be treated as production data.

## Validation

The project has been checked with Django system checks and test suite execution.
