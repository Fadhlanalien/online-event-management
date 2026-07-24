from flask import json, Flask, render_template, request, redirect, url_for, session, flash, make_response
import psycopg
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # change in production

# ------------------- Database connection -------------------
def get_db_connection():
    """Return a PostgreSQL connection using DATABASE_URL env var or fallback."""
    # Use environment variable provided by Render (or set locally)
    database_url = "postgresql://online_event_management_db_user:RUtt08LBEcUcH3TN96O2elmsCMzNRSwK@dpg-d9hpk1epbkes738uukq0-a.virginia-postgres.render.com/online_event_management_db"
    if database_url:
        conn = psycopg.connect(database_url)
    # else:
    #     # Fallback for local development – adjust credentials as needed
    #     conn = psycopg.connect(
    #         host="localhost",
    #         dbname="your_db",
    #         user="your_user",
    #         password="your_password",
    #         port=5432
    #     )
    return conn

# ------------------- No-cache headers -------------------
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# ------------------- Database initialization -------------------
def init_db():
    """Create tables if they don't exist, and insert sample events if empty."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Create users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    year_of_study TEXT NOT NULL,
                    roll_number TEXT NOT NULL,
                    email TEXT NOT NULL,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            """)

            # Create events table with JSONB for form_fields
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    date TEXT,
                    location TEXT,
                    form_fields JSONB NOT NULL
                )
            """)

            # Create registrations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS registrations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    event_id INTEGER NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES events(id),
                    UNIQUE(user_id, event_id)
                )
            """)

            # Insert sample events only if table is empty
            cur.execute("SELECT COUNT(*) FROM events")
            count = cur.fetchone()[0]
            if count == 0:
                events = [
                    ('Tech Conference 2025', '2025-08-20', 'Auditorium',
                     json.dumps(['payment', 'payment_slip', 'special_req'])),
                    ('Entrepreneurship Bootcamp', '2025-09-10', 'Main Hall',
                     json.dumps(['special_req', 't-shirt_size'])),
                    ('Cultural Fest 2025', '2025-11-05', 'Campus Ground',
                     json.dumps(['payment', 'team_name', 'preffered_session']))
                ]
                for ev in events:
                    cur.execute(
                        "INSERT INTO events (name, date, location, form_fields) VALUES (%s, %s, %s, %s)",
                        (ev[0], ev[1], ev[2], ev[3])
                    )
            conn.commit()

# ------------------- Routes -------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/guest_event")
def guest_event():
    return render_template("event_guest.html")

@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
                user = cur.fetchone()
                if user:
                    session['user_id'] = user[0]
                    flash(f"User ID is: {user[0]}")
                    return redirect(url_for('dashboard'))
                else:
                    flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        department = request.form['department']
        year_of_study = request.form['year_of_study']
        roll_number = request.form['roll_number']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO users (full_name, department, year_of_study, roll_number, email, username, password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (full_name, department, year_of_study, roll_number, email, username, password))
                    conn.commit()
                    flash("Signup successful. Please login.")
                    return redirect(url_for('login'))
                except psycopg.IntegrityError:
                    conn.rollback()
                    flash("Username already exists. Try another.")
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT full_name, username FROM users WHERE id=%s", (user_id,))
                user = cur.fetchone()
                if user:
                    full_name, username = user[0], user[1]
                else:
                    full_name = username = "unknown"
        return render_template('dashboard.html', full_name=full_name, username=username)
    return redirect(url_for('login'))

@app.route("/logged_in_event")
def logged_in_event():
    return render_template("event_logged_in.html")

@app.route('/my_event')
def my_event():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT events.name, events.date, events.location
                FROM registrations
                JOIN events ON registrations.event_id = events.id
                WHERE registrations.user_id=%s
            """, (user_id,))
            events = cur.fetchall()
    return render_template('my_event.html', events=events)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if request.method == 'POST':
                username = request.form['username']
                email = request.form['email']
                password = request.form['password']

                if password.strip() == "":
                    cur.execute("SELECT password FROM users WHERE id=%s", (user_id,))
                    password = cur.fetchone()[0]

                cur.execute("""
                    UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s
                """, (username, email, password, user_id))
                conn.commit()
                return redirect(url_for('dashboard'))

            cur.execute("SELECT username, email FROM users WHERE id=%s", (user_id,))
            data = cur.fetchone()
            user_data = {'username': data[0], 'email': data[1]}
    return render_template('edit_profile.html', user_data=user_data)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('home'))

@app.route('/select_event', methods=['GET', 'POST'])
def select_event():
    if 'user_id' not in session:
        flash('Please login to register for an event.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    event_id = request.form['event_id']

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if already registered
            cur.execute("SELECT id FROM registrations WHERE user_id=%s AND event_id=%s", (user_id, event_id))
            registered_event = cur.fetchone()

            # Get event details
            cur.execute("SELECT name, date, location, form_fields FROM events WHERE id=%s", (event_id,))
            event_data = cur.fetchone()

            event_name = event_data[0]
            already_registered = registered_event is not None

            event = {
                'id': event_id,
                'title': event_data[0],
                'date': event_data[1],
                'location': event_data[2],
                'form_fields': event_data[3],   # already a Python list because JSONB is auto-deserialized
                'time': "no time"
            }

            if already_registered:
                flash(f"You have already registered for '{event_name}'!")

    return render_template('register_event.html', event=event, already_registered=already_registered)

@app.route('/register_event', methods=['POST'])
def register_event():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    event_id = request.form['event_id']

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM events WHERE id=%s", (event_id,))
            result = cur.fetchone()
            event_name = result[0] if result else 'unknown event'

            cur.execute(
                "INSERT INTO registrations (user_id, event_id) VALUES (%s, %s)",
                (user_id, event_id)
            )
            conn.commit()

            flash(f'You have successfully registered for "{event_name}"!')
            return redirect(url_for('dashboard'))

# ------------------- Main -------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)   # debug=True for development