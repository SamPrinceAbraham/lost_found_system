from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime
import yagmail
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# ✅ SQLite connection
conn = sqlite3.connect("lost_found.db", check_same_thread=False)
cursor = conn.cursor()

# ✅ Ensure table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    name TEXT,
    description TEXT,
    location TEXT,
    contact TEXT,
    image TEXT,
    date TEXT
)
""")
conn.commit()

# Gmail Setup
sender_email = "lostandfound.act@gmail.com"
app_password = "ohehmwbnkjzgtxgg"  # App password

recipients = [
    "23cse171@act.edu.in", # Tamil Selva
    "23cse153@act.edu.in", # Sathyanesar
    "23cse144@act.edu.in", # R Sanjay
    "23cse135@act.edu.in", # Sam Prince
    "kalarani.cse@act.edu.in" # Kalarani mam
]

# 📧 Send Email with Inline Image
def send_notification_email(name, description, location, contact, item_type, image_filename):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

    # Build HTML email body
    body = f"""<html><body style="font-family: Times New Roman, sans-serif; line-height:1; font-size:18px; color:#000000;">
<div style="font-weight:bold;font-size:16px;">Hello,</div>
<div style="margin:0; padding-bottom:2px; font-size:16px;">
A new item has been reported in the Lost & Found portal.
</div>

<table style="border-collapse: collapse; border-spacing:0; margin:4px 0; font-size:16px; width:100%;">
<tr>
  <td style="padding:2px 6px; font-weight:bold; text-align:left;">Product Category (Lost/Found)</td>
  <td style="padding:2px 6px; text-align:center; width:10px;">:</td>
  <td style="padding:2px 6px; text-align:left;">{item_type}</td>
</tr>
<tr>
  <td style="padding:2px 6px; font-weight:bold; text-align:left;">Name of the Person</td>
  <td style="padding:2px 6px; text-align:center; width:10px;">:</td>
  <td style="padding:2px 6px; text-align:left;">{name}</td>
</tr>
<tr>
  <td style="padding:2px 6px; font-weight:bold; text-align:left;">Description</td>
  <td style="padding:2px 6px; text-align:center; width:10px;">:</td>
  <td style="padding:2px 6px; text-align:left;">{description}</td>
</tr>
<tr>
  <td style="padding:2px 6px; font-weight:bold; text-align:left;">Location</td>
  <td style="padding:2px 6px; text-align:center; width:10px;">:</td>
  <td style="padding:2px 6px; text-align:left;">{location}</td>
</tr>
<tr>
  <td style="padding:2px 6px; font-weight:bold; text-align:left;">Person to be Contacted</td>
  <td style="padding:2px 6px; text-align:center; width:10px;">:</td>
  <td style="padding:2px 6px; text-align:left;">{contact}</td>
</tr>
</table>
"""

    # Footer + Item Image below
    if os.path.exists(image_path):
        body += f"""
<div style="margin-top:10px; text-align:center; font-size:16px; color:#555;">
Thanks,<br>
Lost & Found System</div>

<div style="margin:10px 0; font-weight:bold; font-size:16px; text-align:left;">Item Image:</div>
<img src="cid:{image_filename}" style="max-width:400px; height:auto; border:1px solid #ccc; border-radius:6px;" />
</body></html>
"""
    else:
        body += """
<div style="margin-top:10px; text-align:center; font-size:16px; color:#555;">
Thanks,<br>
Lost & Found System</div>
</body></html>
"""

    # Prepare contents for yagmail
    contents = [yagmail.inline(image_path)] if os.path.exists(image_path) else []
    contents.insert(0, body)

    yag = yagmail.SMTP(sender_email, app_password)
    yag.send(
        to=recipients,
        subject=f"Lost & Found Notification - {item_type}",
        contents=contents
    )


# 🏠 Home Page
@app.route('/')
def index():
    return render_template('index.html')

# 🧍 Lost Form
@app.route('/lost', methods=['GET', 'POST'])
def lost():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        contact = request.form['contact']

        # ✅ Handle both file upload and camera capture
        if 'camera_image' in request.form and request.form['camera_image']:
            img_data = request.form['camera_image'].split(",")[1]
            filename = f"camera_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(img_data))
        else:
            image = request.files['image']
            filename = image.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)

        cursor.execute(
            "INSERT INTO items (type, name, description, location, contact, image, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('Lost', name, description, location, contact, filename, datetime.now())
        )
        conn.commit()

        send_notification_email(name, description, location, contact, "Lost", filename)
        return redirect(url_for('index'))

    return render_template('lost.html')

# 🧳 Found Form
@app.route('/found', methods=['GET', 'POST'])
def found():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        contact = request.form['contact']

        # ✅ Handle both file upload and camera capture
        if 'camera_image' in request.form and request.form['camera_image']:
            img_data = request.form['camera_image'].split(",")[1]
            filename = f"camera_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(img_data))
        else:
            image = request.files['image']
            filename = image.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)

        cursor.execute(
            "INSERT INTO items (type, name, description, location, contact, image, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('Found', name, description, location, contact, filename, datetime.now())
        )
        conn.commit()

        send_notification_email(name, description, location, contact, "Found", filename)
        return redirect(url_for('index'))

    return render_template('found.html')

# 👁️ View All
@app.route('/view')
def view_items():
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return render_template('view_items.html', items=items)

# ❌ Delete
@app.route('/delete/<int:id>', methods=['POST'])
def delete_item(id):
    cursor.execute("SELECT image FROM items WHERE id = ?", (id,))
    result = cursor.fetchone()

    if result:
        image_filename = result[0]
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        cursor.execute("DELETE FROM items WHERE id = ?", (id,))
        conn.commit()

    return redirect(url_for('view_items'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
