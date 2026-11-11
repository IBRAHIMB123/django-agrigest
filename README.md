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

6. (Optional) Seed demo data for local development only:

```bash
python manage.py seed_demo_data
```

The demo account has no usable password unless `AGRIGEST_DEMO_PASSWORD` is set before running the command. The command refuses to run when `DJANGO_DEBUG=0`.

7. Start the development server:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Production deployment on Render

AgriGest is a Django application, so it needs a Python web service rather than a static-site host such as Vercel or Netlify. The root-level `render.yaml` configures a Render web service, PostgreSQL, WhiteNoise static files, a persistent disk for uploaded media, and migrations before each deployment.

1. Push this repository to GitHub.
2. In Render, choose **New > Blueprint**, connect the repository, and review the resources and costs defined by `render.yaml` before creating them. The web service, PostgreSQL database, and persistent disk are not necessarily free.
3. Wait for the first deployment to finish, then create an administrator from the Render Shell:

   ```bash
   python config/manage.py createsuperuser
   ```

4. If you use a custom domain, add it to `DJANGO_ALLOWED_HOSTS` and add its HTTPS origin to `DJANGO_CSRF_TRUSTED_ORIGINS` (for example, `https://agrigest.example.com`).
5. Configure SMTP environment variables in Render if password-reset emails should be delivered. Do not use demo seed data or demo credentials in production.

The Render database starts empty; local SQLite data is not copied automatically. Uploaded media is stored on the persistent disk, but should still be backed up separately.

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
