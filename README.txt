SR REAL ESTATE — WEBSITE PACKAGE

Brand: SR Real Estate
Tagline: We make your dream house.
Services: Buy • Sell • Rent
Location: Udupi, Karnataka

PROJECT STRUCTURE
- app.py: Flask application and property/admin routes
- templates/: all HTML templates
- static/style.css: website styling
- static/uploads/: uploaded property photos
- requirements.txt: Python dependencies
- Procfile: Render start command

RUN LOCALLY ON WINDOWS
1. Install Python 3.12 or newer.
2. Open this project folder in VS Code.
3. Open Terminal > New Terminal.
4. Run: py -m venv venv
5. Run: .\venv\Scripts\activate
6. Run: pip install -r requirements.txt
7. Run: python app.py
8. Open http://127.0.0.1:5000

RENDER DEPLOYMENT
Build command: pip install -r requirements.txt
Start command: gunicorn app:app
Environment variables required:
- SECRET_KEY: use a long random secret value
- ADMIN_USERNAME: choose a private username
- ADMIN_PASSWORD: choose a strong unique password

ADMIN
Open /admin/login on your website. Do not use the default credentials in production.

BUSINESS DETAILS
Phones: +91 96202 53110 / +91 96114 13920
WhatsApp: +91 96114 13920
Address: Poonja Towers, 3rd Floor, Near UB Towers, Opposite Giriyas Udupi Branch, Kalpana Bus Stop, Udupi District.
Hours stated for Monday–Saturday: 9:00 AM–1:30 PM and 3:00 PM–8:00 PM. Confirm Sunday hours before publishing them.

IMPORTANT PRODUCTION NOTES
This package uses SQLite and stores uploaded photos in static/uploads. On a typical ephemeral hosting filesystem, data and photos may be lost after restarts or redeployments. Before relying on this site for real listings and enquiries, configure persistent storage or a managed database and persistent image storage. The property listing form sends an enquiry to the site; it does not automatically publish a listing. Admin must add approved listings.
