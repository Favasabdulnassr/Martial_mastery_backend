# 🥋 Martial Mastery Backend

Martial Mastery is a Django-based backend for an online martial arts training platform. It supports **students, tutors, and admins**, allowing students to purchase and watch course tutorials, interact with tutors, and participate in structured learning. Tutors can create and manage courses, while admins oversee and verify platform activities.

---

## 🌟 Features

### 👤 User (Student)
- Register and log in with email and password
- Browse and purchase available courses
- View tutorial videos for enrolled courses
- One-to-one chat with assigned tutor after purchase
- Participate in a comment section under each video
- Report inappropriate courses or content

### 🎓 Tutor
- Register and log in as a tutor
- Create and manage courses
- Upload videos related to each course
- Mark courses as **complete** for admin review
- View list of students enrolled in their courses
- Manage personal wallet and request withdrawals

### 🛠️ Admin
- Dashboard for managing users and tutors
- Verify or reject courses marked as complete by tutors
- View separate lists of students and tutors
- Monitor reported courses

---

## 🧱 Project Structure

- `user_auth/` – Handles authentication and custom user model (student, tutor, admin)
- `Courses/` – Course creation, video uploads, and management
- `payment/` – Handles Stripe integration and course purchases
- `chat/` – Real-time one-to-one chat using Django Channels
- `comments/` – Comment system under tutorial videos
- `dashboard/` – Admin dashboard with verification and monitoring features
- `ReportWallet/` – Course reporting and tutor wallet functionality
- `notifications/` – In-app notification handling

---

## 🛠️ Technologies Used

- **Django 5.1.3**
- **PostgreSQL**
- **Django REST Framework**
- **Django Channels** for WebSocket chat
- **Cloudinary** for video/media storage
- **Stripe** for payment integration
- **JWT (Simple JWT)** for secure authentication
- **CORS Headers** for frontend communication
- **.env** file for managing secrets

---

## ⚙️ Setup Instructions

### 1. Clone the Repository


```bash
git clone https://github.com/yourusername/martial-mastery-backend.git
cd martial-mastery-backend


2. Create Virtual Environment and Install Dependencies
bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt


3. Configure Environment Variables
Create a .env file in the root directory and set the following:

env
MY_SECRET_KEY=your_secret_key

MY_EMAIL=your_email@gmail.com
MY_EMAIL_HOST_PASSWORD=your_email_password
MY_EMAIL_PORT=587

CLOUD_NAME=your_cloudinary_name
API_KEY=your_cloudinary_key
API_SECRET=your_cloudinary_secret

STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_ENDPOINT_SECRET=your_stripe_webhook_secret

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

MY_TWILIO_AUTH_TOKEN=your_twilio_token
MY_TWILIO_NUMBER=your_twilio_number
MY_ACCOUNT_SID=your_twilio_sid


4. Run Migrations and Create Superuser

bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


5. Run the Server
bash
python manage.py runserver


📁 Media & Static Files
Media Files: Uploaded videos are stored in Cloudinary

Static Files: Default static directory used (custom configuration can be added)

🔐 Authentication
JWT-based authentication using Simple JWT

Token refresh and rotation enabled

Custom user model with email as USERNAME_FIELD