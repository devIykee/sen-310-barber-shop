# Fresh Fade Barbershop — Appointment Scheduling System

Fresh Fade Barbershop is a Django web application for running a small barbershop’s appointment schedule. It has two practical sides:

- **Customer side:** people can create an account, see the available services, choose a barber, select a date and time, make a booking, review their bookings, and cancel an upcoming booking.
- **Business side:** the owner uses Django’s protected administration area to manage barbers, services, customers, bookings, completed work, and blocked-out periods.

The application was designed around one important business rule: **a barber cannot have two active appointments whose times overlap.** The booking form calculates the appointment end time from the selected service duration and validates the whole time range before saving anything.

## Live system

The Render deployment is a Web Service. Its address is shown in the Render dashboard under the service name. Record the final address here before submission:

```text
Live URL: https://<your-render-service-name>.onrender.com
Administration: https://<your-render-service-name>.onrender.com/admin/
```

Render’s free tier can take a short time to wake after inactivity. If the first request is slow, wait for it to finish loading rather than refreshing repeatedly.

## What each part of the system represents

| Real barbershop concept | Django model | Purpose |
| --- | --- | --- |
| The shop itself | `Business` | Stores name, description, address, working hours, and contact details. |
| A haircut or grooming option | `Service` | Stores name, duration in minutes, price, active state, and its business. |
| A barber | `Staff` | Stores barber name, role, active state, business, and the services the barber can perform. |
| A registered client | Django `User` + `Customer` | `User` handles secure authentication; `Customer` is a one-to-one profile containing a phone number. |
| A customer reservation or owner time block | `Appointment` | Stores customer, barber, service, date, start and end times, status, notes, and creation time. |

The first migration seeds the catalogue with Fresh Fade Barbershop, **Classic Haircut** (30 minutes, ₦5,000), **Haircut and Beard Trim** (45 minutes, ₦7,500), and **Tunde Adeyemi** as a Senior Barber. The seeded barber is assigned to both services.

## Roles and access

### Customer account

A customer account is created from **Register** in the site navigation.

1. Open the live site.
2. Select **Register**.
3. Enter a username, email address, optional phone number, and password twice.
4. Submit the form. The system creates both a Django `User` and its linked `Customer` profile, then signs the person in automatically.
5. The customer can now use **Book now** and **My appointments**.

Customers can only see appointments that belong to their own signed-in account. The cancellation URL checks the appointment’s `customer` field, so a logged-in customer cannot cancel another customer’s appointment merely by changing a URL.

### Barbers and business administration

The `Staff` model represents barbers for scheduling purposes. A staff record itself is **not** a login account. This is intentional for this version: the person operating the schedule signs in as the **Business Admin** and manages staff records through Django admin.

To log in as the barbershop owner/admin:

1. In Render, open the deployed Web Service.
2. Open the service’s **Shell** tab.
3. Run:

   ```bash
   python manage.py createsuperuser
   ```

4. Enter a username, email, and a strong password when prompted. These are the admin credentials; keep them private.
5. Go to `https://<your-render-service-name>.onrender.com/admin/`.
6. Sign in with that superuser username and password.

This admin account is the appropriate answer when demonstrating “how the barber logs in.” It gives the business owner access to every management screen. The visible `Staff` entries (for example, Tunde Adeyemi) are the barbers customers choose while booking; they do not need separate passwords in the current requirements.

## Customer booking walkthrough

This is the main path to demonstrate.

1. From the home page, inspect the service cards. Each card shows its duration and price.
2. Register or log in as a customer.
3. Click **Book now**.
4. Select a service. This determines the duration: for example, a 30-minute Classic Haircut started at 10:00 ends at 10:30.
5. Select a barber. The form only accepts a barber assigned to the chosen service.
6. Select a future date and a start time.
7. Click **Confirm booking**.
8. If the slot is free, the system saves a `confirmed` appointment and redirects to **My appointments** with an on-screen confirmation.
9. On **My appointments**, the customer sees service, barber, date, start/end times, and status.
10. Click **Cancel** to cancel a pending or confirmed appointment. The record is preserved for audit/history but its status becomes `cancelled`, so that time no longer blocks new bookings.

### A useful double-booking demonstration

To prove the scheduling rule during a demonstration:

1. Book Tunde for Classic Haircut on a future date at 10:00. This occupies 10:00–10:30.
2. Attempt a second booking with Tunde at 10:15 on the same date.
3. The app rejects it with a message that the time has been taken.
4. Try 10:30 instead. This is accepted because one appointment ends exactly as the next one begins; those ranges do not overlap.

The overlap condition is:

```text
existing start time < requested end time
AND existing end time > requested start time
```

That formula catches full overlaps, partial overlaps, and appointments contained inside another one. Cancelled appointments are deliberately ignored, allowing the released time to be booked again.

## Business admin walkthrough

After logging in at `/admin/`, the administration home lists Business, Services, Staff, Customers, and Appointments.

### Manage services

Open **Services** to add, edit, or deactivate offerings.

- **Business:** choose Fresh Fade Barbershop.
- **Name:** e.g. “Kids Haircut.”
- **Duration minutes:** used by the booking engine to calculate end time.
- **Price:** current cost in naira.
- **Active:** untick it to hide an old service from customer booking without deleting historical records.

When a new service is added, open the relevant **Staff** record and assign that service in its multi-select Services field. Customers cannot book a service with a barber who has not been assigned that service.

### Manage barbers

Open **Staff** and select **Add Staff**. Set the business, barber name, role, and active state, then select every service that barber is qualified to perform. Unticking **Active** removes a barber from the public booking form while retaining their appointment history.

### Review appointments and mark work complete

Open **Appointments**. The list shows barber, customer, service, date, start time, and status. Use Django admin’s filters for status, date, and staff to answer questions such as “what is booked today?”

After serving a customer, select the appointment(s), choose **Mark selected appointments complete** from the Actions drop-down, then click **Go**. This changes the status to `completed`.

### Block a barber’s unavailable time

To prevent customers booking a barber during a break, leave, or a walk-in-only period:

1. Open **Appointments** and choose **Add Appointment**.
2. Leave **Customer** and **Service** empty.
3. Select the relevant Staff member.
4. Enter the unavailable date, start time, end time, and choose status **Blocked**.
5. Optionally write a reason in Notes, such as “Lunch break” or “Annual leave.”
6. Save.

The blocked record is treated as an active appointment by the same conflict query, so a normal customer booking that overlaps it cannot be confirmed.

## How the code is organised

```text
freshfade/                 Django project configuration
  settings.py              Database, security, static files, allowed hosts
  urls.py                  Routes /admin/ and the booking application
booking/                   Main application
  models.py                Business, Service, Staff, Customer, Appointment
  forms.py                 Registration and validated appointment form
  views.py                 Customer-facing page and booking actions
  admin.py                 Owner/admin configuration and completion action
  urls.py                  Public URL routes
  templates/               Bootstrap-based pages
  tests/test_booking.py    Automated booking-rule tests
docs/                      SEN 310 report source, PDF, Mermaid source, diagrams
build.sh                   Render build steps
Procfile                   Gunicorn server command
render.yaml                Render blueprint configuration
requirements.txt           Python dependencies
```

### URL map

| URL | View / function | Who uses it |
| --- | --- | --- |
| `/` | Home page | Everyone |
| `/register/` | Registration form | New customers |
| `/login/` | Django login view | Existing customers and admins |
| `/logout/` | Django logout view | Signed-in users |
| `/book/` | Appointment form | Signed-in customers |
| `/appointments/` | Customer appointment list | Signed-in customers |
| `/appointments/<id>/cancel/` | Cancellation action | Owner of that appointment |
| `/admin/` | Django administration | Business Admin / superuser |

## Booking validation in detail

The form and model work together so validation is not only a front-end check.

1. `AppointmentForm` accepts service, staff, date, and start time.
2. The form verifies that the chosen staff member is linked to the chosen service.
3. It calculates `end_time` by adding `Service.duration_minutes` to the submitted start time.
4. It creates a candidate `Appointment` and calls Django’s model validation.
5. `Appointment.clean()` rejects an end time before or equal to start time, a start time in the past, an unqualified barber/service pairing, or an overlapping active appointment.
6. The booking view repeats `full_clean()` inside `transaction.atomic()` immediately before saving. This keeps validation close to the database write and turns a late conflict into a friendly error instead of saving an invalid reservation.

Appointment statuses have the following meanings:

| Status | Meaning | Blocks a new booking? |
| --- | --- | --- |
| `pending` | Reservation awaits a decision | Yes |
| `confirmed` | Normal accepted customer booking | Yes |
| `cancelled` | Customer or owner released the time | No |
| `completed` | Service has been delivered | Yes as historical record; it is normally in the past |
| `blocked` | Owner-created unavailable period | Yes |

## Local installation and running

The app uses Python 3.11 or newer. SQLite is used locally, so no database server is needed for development.

```bash
git clone https://github.com/devIykee/sen-310-barber-shop.git
cd sen-310-barber-shop
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. To get an owner account locally, run `python manage.py createsuperuser`, then sign in at `http://127.0.0.1:8000/admin/`.

To run the automated tests:

```bash
python manage.py test
```

The tests in `booking/tests/test_booking.py` verify two essential safeguards:

- a second appointment that overlaps an existing booking for the same barber is rejected;
- an appointment whose date/time is in the past is rejected.

## Deployment on Render

This project is deployed as a **Web Service**, not a Static Site.

Render runs the following sequence:

1. Build command: `pip install -r requirements.txt && bash build.sh`
2. `build.sh` runs `collectstatic --no-input` so CSS/static assets are ready, then runs `migrate` to create or update database tables and insert the initial business/service/staff records.
3. Start command: `gunicorn freshfade.wsgi:application`
4. Gunicorn serves Django; WhiteNoise serves collected static files.

The required Render environment variables are:

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | Generate a unique value in Render; never commit an actual production secret. |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` (or add your custom domain too) |
| `DATABASE_URL` | Optional for SQLite, but set automatically when a Render PostgreSQL database is attached. |

`freshfade/settings.py` reads `DATABASE_URL` through `dj-database-url`. Without it, local development uses SQLite. With it, a hosted PostgreSQL URL is used automatically. `DEBUG` is false by default and production security settings include secure cookies, HTTPS redirection behind Render’s proxy, HSTS, and a restricted allowed-host list.

## SEN 310 submission materials

The complete written deliverable is available in [`docs/SEN310_Documentation.pdf`](docs/SEN310_Documentation.pdf). Its editable Markdown source is [`docs/SEN310_Documentation.md`](docs/SEN310_Documentation.md). It includes:

1. Customer and administrator user stories.
2. Use-case diagram and use-case descriptions.
3. Appointment booking sequence diagram and explanation.
4. Class diagram and model relationship explanation.
5. A hosted-link section to update with the actual Render URL.

The Mermaid diagram definitions are retained in `docs/diagrams/*.mmd`; rendered SVG versions are embedded in the PDF as images.

## Points to explain confidently in a project defence

- Django’s built-in `User` model was reused for password hashing, authentication, sessions, and permissions instead of implementing insecure custom authentication.
- `Customer` is a profile model connected one-to-one to `User`, keeping customer-specific information separate from Django’s core authentication data.
- A service duration, rather than manually typed end times, determines appointment length. That is why bookings are consistent and why the overlap calculation is reliable.
- `Staff.services` is many-to-many because one barber can offer several services and a service can be provided by several barbers.
- Cancellation changes status rather than deleting a row. This preserves business history while making the slot available.
- The Django admin was used for owner functionality because it already provides authentication, permissions, filters, search, forms, and safe CRUD screens. This is appropriate for an internal business management tool.
- The model’s `clean()` method is the central business-rule boundary; forms call it before a customer booking and Django admin calls model validation when staff manage records.
- Production setup differs from local setup: local SQLite supports quick development; Render can use PostgreSQL through `DATABASE_URL`, while WhiteNoise handles static files and Gunicorn runs the WSGI app.
