@app.route('/select_event', methods=['POST'])
def select_event():
    event_id = request.form.get("event_id")

    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, date, location, form_fields FROM events WHERE id=?", (event_id,))
        row = cursor.fetchone()

    if not row:
        flash("Event not found")
        return redirect(url_for("event"))

    event = {
        "id": event_id,
        "title": row[0],
        "date": row[1],
        "location": row[2],
        "time": "No Time",
        "form_fields": json.loads(row[3])  # Load JSON list
    }

    return render_template("register_event.html", event=event)
