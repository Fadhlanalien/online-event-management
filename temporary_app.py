from flask import json, Flask, render_template, request, redirect, url_for, session, flash, make_response
import sqlite3
import os
                                                    # Flask - let python act like a web server
                                                    # render_template - Loads HTML files from a folder named templates
                                                    # request - Lets you access form data (like POST or GET values from the user).

app = Flask(__name__)   # creates a web app starting from this file.

app.secret_key = 'your_secret_key'  # needed for session (move under app = falsk(__name__) later)
                                    # sets a secret key for the Flask app - doubt

@app.after_request                      # It tells Flask to run this function after every request is processed but before sending the response to the browser
                                        # 1. User visits /login → Flask runs login() function.
                                        #   - If it's a POST request, it processes form data.
                                        #   - Finally, login() returns a value like render_template(...) or redirect(...).
                                        #
                                        # 2. Flask takes that return value and creates a Response object.
                                        #      - This object contains HTML + headers + status code, etc.
                                        #
                                        # Before sending the response to the browser, Flask triggers @app.after_request.
                                        # - It calls add_no_cache_headers(response) with that Response object.
                                        
def add_no_cache_headers(response):     # function with response as a parameter
                                        # response variable represents the HTTP response that Flask is about to send to the browser.
                
                
                # cache - Cache is a temporary storage that saves copies of files or data so that future requests can be served faster.

                # caching - Caching is the process of storing frequently used data in cache
                
                
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'        # headers['cache-control'] - controls caching rules for modern browsers
                                                                                                # no-store - Browser should not store any part of the page
                                                                                                # no=cache - Browser must always check with the server(is the cache is stil valid or nor, is the cached datas were modified or nor) before showing the page
                                                                                                # 'no-store' and 'no-cache' often combined for full no-caching behavior.
                                                                                                # must-revalidate - If cached, browser must verify (if the cache is expired, Without this, some browsers may show an expired page offline) with the server before using it 
                                                                                                # max-age=0 - Cache expires immediately(for modern browsers)
                                                                                                
    response.headers['Pragma'] = 'no-cache'                     # headers['Pragma'] - controls caching rules for old browsers
                                                                # It ensures that even old browsers don’t cache the page.
    
    
    response.headers['Expires'] = '0'                           # headers['expires'] - tells the browser how long the response can be cached.
                                                                # Tells the browser that the page has already expired (valid until time 0). - for old browsers
    return response

# Database initialization (run once)
def init_db():                                                      # function for create database, it creates the table named user if the table doesn't exist
                                                                    # with the fields ID, username and password
    
    
    with sqlite3.connect('users.db') as conn:
        
        # create users table
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        department TEXT NOT NULL,
                        year_of_study TEXT NOT NULL,
                        roll_number TEXT NOT NULL,
                        email TEXT NOT NULL,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')
        
        # create event table
        conn.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        date TEXT,
                        location TEXT,
                        form_fields TEXT NOT NULL)''')
        
        # create registration table
        conn.execute('''CREATE TABLE IF NOT EXISTS registrations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            event_id INTEGER NOT NULL,
                            FOREIGN KEY (event_id) REFERENCES events(id),
                            unique(user_id, event_id))''')
        

        conn.commit()       # commit the tabele creation (save)
        
    

        
        
         # Insert sample events (only if events table is empty)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")       # Counts the number of rows in the events table
        
        count = cursor.fetchone()[0]                        # Fetches the count result (first column of first row)

        if count == 0:                                      # if the count is empty (no values one event table)
            events = [
                ('Tech Conference 2025', '2025-08-20', 'Auditorium', json.dumps(['payment', 'payment_slip', 'special_req'])),
                ('Entrepreneurship Bootcamp', '2025-09-10', 'Main Hall', json.dumps(['special_req', 't-shirt_size'])),
                ('Cultural Fest 2025', '2025-11-05', 'Campus Ground', json.dumps(['payment', 'team_name', 'preffered_session']))
            ]
            cursor.executemany("INSERT INTO events (name, date, location, form_fields) VALUES (?, ?, ?, ?)", events)    # inserts all event records to event table from above events dictionary
            conn.commit()

@app.route("/")         # it tells, When the user opens the main homepage (i.e., /) in the browser, run the function below.
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
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()                  # creates a cursor object, which acts like a "pointer" or controller for executing SQL commands
            
            cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))         # This line executes a SQL query to find a row in the users table
                                                                                                                # where both the username and password match the values entered by the user.
            user = cursor.fetchone()                # fetches the first matching row from the result of the SELECT query and assign it to 'user'
            if user:
                session['user_id'] = user[0]          # Stores user_id in the session cookie
                
                flash(f"User ID is: {user[0]}")     # prints this message in dashboard page
                
                return redirect(url_for('dashboard'))   # it allows to run the dashboard function before going to dashboard page

            else:
                flash("Invalid credentials.")
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])                                                              
def signup():                                           
    if request.method == 'POST':  
        full_name = request.form['full_name']
        department = request.form['department']
        year_of_study = request.form['year_of_study']
        roll_number =  request.form['roll_number']
        email = request.form['email']                      
        username = request.form['username']             # intialize the password from the form to paswword
        password = request.form['password']
        
        with sqlite3.connect('users.db') as conn:       # opens the users.db and asigns it to the conn
            try:
                conn.execute("INSERT INTO users (full_name, department, year_of_study, roll_number, email, username, password) VALUES (?, ?, ?, ?, ?, ?, ?)", (full_name, department, year_of_study, roll_number, email, username, password))  
                conn.commit()                               #  saves the changes to the database permanently.
                flash("Signup successful. Please login.")   # displays the message inside the qoute using the flask's flash system
                return redirect(url_for('login'))
            
                                                            # if enetered username wasn't unique it directs to the below except case
            
            except sqlite3.IntegrityError:                      # doubt - what is the use case of 'sqlite3.IntegrityError'
                flash("Username already exists. Try another.")
    return render_template('signup.html')                   # directs to the sign-up file (refresh the page again)




@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:           # it is the current username available in session dictionary (assigned it while logging in - means user logged in)
        
        user_id = session['user_id']
        
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("select full_name, username from users where id=?", (user_id,))
            user = cursor.fetchone()
            if user:
                full_name = user[0]
                username = user[1]
            else:
                full_name = "unknown"
                username = "unknown"
        
            return render_template('dashboard.html', full_name=full_name, username=username)      # directs to dashboard page and assign the current usernama for user variable
    return redirect(url_for('login'))               # redirect the user to login page untill the above if condition becoming true

@app.route("/logged_in_event")
def logged_in_event():
    return render_template("event_logged_in.html")

@app.route('/my_event')
def my_event():
    if 'user_id' not in session:                   # if the user not logged in
        return redirect(url_for('login'))       # directs user to login page

    user_id = session['user_id']                   # get the value for user_id key from session dictionary and assigns it to user_id  (session['user'] was defined while logging in)

    # Assuming you have a table `registrations` that stores user_name and event_id
    conn = sqlite3.connect('users.db')              # start the database connection
    cursor = conn.cursor()
    cursor.execute("""select events.name, events.date, events.location from registrations
                   join events on registrations.event_id = events.id
                   where registrations.user_id=?""", (user_id,))       
    
    events = cursor.fetchall()                                                              # fetch all the values stored in cursor (all field values from registartion table  for user_id='user_id' ) and assigns it to events
    
    conn.close()                                                                            # close the db connection

    return render_template('my_event.html', events=events)                  # saves the events to event and direct the user to my_event page



@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:                   # if user not logged in
        
        
        return redirect(url_for('login'))       # runs the login function

    user_id = session['user_id']
    conn = sqlite3.connect('users.db')      # turn on the connection to database
    cursor = conn.cursor()

    if request.method == 'POST':                    # if the form submitted
        
        username = request.form['username']         # get the username from form and assigns it to username
        email = request.form['email']
        password = request.form['password']
        
        # If password field is empty, fetch the old password
        if password.strip() == "":
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
            password = cursor.fetchone()[0]  # Keep the old password

        cursor.execute("""
            UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?       
        """, (username, email, password, user_id))            # updates the value of username, email, and password to user provided name (now the username also new)
        conn.commit()                               # saves the changes
        conn.close()
        
        return redirect(url_for('dashboard'))

    cursor.execute("SELECT username, email FROM users WHERE id = ?", (user_id,))        # before the submission select usernama and email (current or old) and assigns it to cursor
    
    data = cursor.fetchone()                                                                    #  assign the fetched datas to data                                                               
    conn.close()

    user_data = {'username': data[0], 'email': data[1]}         # username = data[0] = username selected from table, email = data[1] = fetched email from table
    
    return render_template('edit_profile.html', user_data=user_data)    # directing to edit_profile page and pass the user_data too


@app.route('/logout')       # runs the below function when the user enters the logout page
def logout():
    session.clear()               # # Remove all values currently stored in the session
    flash("You have been logged out.")      # It stores the message temporarily so it can be shown on the next page you render (usually the login page).
    return redirect(url_for('home'))       # allows to run the login function while the user is in logout page




@app.route('/select_event', methods=['GET', 'POST'])      # when user get into register_event page it runs the below function
                                                            # also when user submitted the form it allows to get the data from form
def select_event():
    if 'user_id' not in session:                           # if the username is not in session dictionary (user not logged in)
        flash('Please login to register for an event.')     # store this message temporarily and print it om next page
        return redirect(url_for('login'))                   # allows to run the login function

    user_id = session['user_id']                      # fetches the user from session dictionary and assigns it to username
    
    event_id = request.form['event_id']             # gets the event_id from the event page, when user click on 'register' on patcicular event

    
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('select id from registrations where user_id = ? and event_id = ?', (user_id,event_id))
        registered_event = cursor.fetchone()
        
        
    
    
        
        cursor.execute('select name, date, location, form_fields from events where id=?', (event_id,))
        event_data = cursor.fetchone()
        
        event_name = event_data[0]
        
        if registered_event:
            flash(f"You have already registered for '{event_name}'!")
        
            
        already_registered = registered_event is not None
        
        event = {
            'id' : event_id,
            'title' : event_data[0],
            'date' : event_data[1],
            'location' : event_data[2],
            'form_fields' : json.loads(event_data[3]),
            'time' : "no time"
            }
        
    return render_template('register_event.html', event = event, already_registered = already_registered)


@app.route('/register_event', methods=['POST'])
def register_event():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    event_id = request.form['event_id']
    
    
    
    # insert into database
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()

        # Get event name from the events table
        cursor.execute("SELECT name FROM events WHERE id = ?", (event_id,))     # this comment select the event name by using the event_id and preparing it to hold the result set of that query.
        result = cursor.fetchone()          # fetches the first row returned by the previous SELECT query and assign it to result (in this case it returns a tuple with one value, which is the event name)
        
        if result:
            event_name = result[0]          # example,  result	 = ('Coding Contest',), result[0] =	'Coding Contest'
        else:
            event_name = 'unknown event'

        # Insert registration
        cursor.execute(                                                         # inser the username and event_id to registration table
            "INSERT INTO registrations (user_id, event_id) VALUES (?, ?)",(user_id, event_id))

        conn.commit()

        flash(f'You have successfully registered for "{event_name}"!')
    
    
        return redirect(url_for('dashboard'))







if __name__ == "__main__":  # this line allows, Only run this block of code if this file is being run directly, not imported as a module in another file.
    
    
    # if os.path.exists("users.db"):
    #     os.remove("users.db")  # ❗ Deletes the database file — only use for development/testing
    
    init_db()
    
    app.run(host="0.0.0.0", port=5000)
    
    # app.run(debug=True)     # Starts the Flask development server
                            # debug=True enables auto-reload and detailed error pages