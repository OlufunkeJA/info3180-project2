# INFO3180 Project 2 - Group #02
## DriftDater
A social matching application.

## Group Members
- Olufunke Ogunde - Project Manager & Frontend Lead
- Christoff Cowan - Frontend Lead
- Orville Daley - Backend Lead
- Delmika Johnson - QA & Testing Lead

## Features

### User Authentication
- Register new accounts with email, handle, password, and profile details.
- Login, logout, and session persistence using cookies.
- Flash-style feedback for successful login/logout and form actions.

### Profiles
- Create and edit a member profile.
- Upload an avatar image and display it across the app.
- Include personal details such as full name, birthdate, gender, seeking preference, location, job title, education, interests, and "about me".
- Set profile visibility and search filters.
- Discover profiles with advanced search by location, age range, interests, gender, job title, and education.
- Matching is scored by location proximity, age range preference, shared interests, and profile similarity in job/education.
- Sort discovered profiles by newest or most similar and save bookmarked favorites for later.

### Matching & Connections
- Browse visible profiles filtered by gender preference and swipe status.
- Like, dislike, or pass on profiles.
- Automatic connection creation when both users like each other.
- View matches and start conversations from the matches page.

### Messaging
- Conversation list for all connected users.
- Send and receive messages in real time with timestamps.
- Report or block users directly from the message view.

### Notifications
- Unread notification count shown in the header.
- Notification list for new messages, connections, and other account events.
- Mark notifications as read individually or all at once.

### Moderation
- Report users for spam, harassment, fake accounts, inappropriate behavior, or other reasons.
- Block and unblock accounts to prevent unwanted interactions.

### Preferences & UI
- Light/dark theme toggle stored locally.
- Responsive interface using Vue 3 and Vite.

## Tech Stack
- Frontend: Vue 3, Vue Router, Vite
- Backend: Flask, SQLAlchemy, Flask-WTF, Flask-Migrate
- Database: PostgreSQL
- File uploads: Cloudinary support

## Project Structure

- `app/` - Flask backend package
  - `routes/` - API route definitions
  - `models.py` - database models and serialization methods
  - `forms.py` - validation forms for login, register, profile, and messaging
- `src/` - Vue frontend
  - `views/` - page views for login, signup, dashboard, matches, messages, profile, edit profile, notifications
  - `components/` - reusable UI components such as header, footer, login/signup forms
  - `services/` - API and session helpers
- `migrations/` - database migration scripts
- `uploads/` - user profile image uploads

## Setup Instructions

### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create or update `.env` with required values:
```env
DATABASE_URL=postgresql://username:password@localhost/database_name
UPLOAD_FOLDER=./uploads
# Optional Cloudinary values
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

Run the backend server:
```bash
flask --app app --debug run
```

### Frontend
```bash
npm install
npm run dev
```

Open the Vite development URL shown in the terminal.

## Database Seeding

A seed SQL file is available at `seed_accounts_profiles.sql` for populating sample accounts and profiles.

Example:
```bash
psql postgresql://username:password@localhost/database_name -f seed_accounts_profiles.sql
```

## API Overview

### Authentication
- `POST /api/register` - create account and profile
- `POST /api/login` - login user
- `POST /api/logout` - logout user
- `GET /api/session` - check current session

### Profiles
- `POST /api/profile` - create member profile
- `GET /api/profile` - get current user profile
- `PUT /api/profile` - update profile
- `GET /api/profiles` - browse matching profiles
- `GET /api/profiles/<id>` - view profile details
- `GET /api/interests` - list interests

### Matching & Connections
- `POST /api/profiles/<id>/like` - like/dislike/pass a profile
- `GET /api/connections` - list current connections
- `GET /api/conversations` - list conversations

### Messaging
- `GET /api/connections/<id>/messages` - fetch conversation messages
- `POST /api/connections/<id>/messages` - send a message

### Notifications
- `GET /api/notifications` - list notifications
- `GET /api/notifications/unread-count` - unread count
- `PUT /api/notifications/<id>/read` - mark one notification read
- `PUT /api/notifications/read-all` - mark all notifications read

### Moderation
- `POST /api/accounts/<id>/report` - report a user
- `POST /api/accounts/<id>/block` - block a user
- `DELETE /api/accounts/<id>/unblock` - unblock a user
- `GET /api/blocks` - list blocked accounts

## Notes
- The frontend expects the backend API to run on the same origin or be proxied appropriately.

## Known issues / future improvements
???????????????

