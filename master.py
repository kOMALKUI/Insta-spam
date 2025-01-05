import os
import time
from flask import Flask, request, redirect, url_for, flash, render_template_string
from werkzeug.utils import secure_filename
from instagrapi import Client

app = Flask(__name__)
app.secret_key = "your_secret_key"
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML Template directly integrated
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MASTER INSTGRAM</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: blue;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: pink;
        }
        .container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: pink;
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: bold;
            margin: 10px 0 5px;
            color: pink;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
            background-color: yellow;
        }
        input:focus, select:focus, button:focus {
            outline: none;
            border-color: pink;
            box-shadow: 0 0 5px rgba(255, 105, 180, 0.5);
        }
        button {
            background-color: pink;
            color: blue;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #ff69b4;
        }
        .message {
            color: red;
            font-size: 14px;
            text-align: center;
        }
        .success {
            color: green;
            font-size: 14px;
            text-align: center;
        }
        .info {
            font-size: 12px;
            color: #777;
            margin-bottom: -10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>MASTER INSTAGRAM</h1>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter your username" required>

            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter your password" required>

            <label for="choice">Send To:</label>
            <select id="choice" name="choice" required>
                <option value="inbox">Inbox</option>
                <option value="group">Group</option>
            </select>

            <label for="target_username">Target Username (for Inbox):</label>
            <input type="text" id="target_username" name="target_username" placeholder="Enter target username">

            <label for="thread_id">Thread ID (for Group):</label>
            <input type="text" id="thread_id" name="thread_id" placeholder="Enter group thread ID">

            <label for="haters_name">Haters Name:</label>
            <input type="text" id="haters_name" name="haters_name" placeholder="Enter hater's name" required>

            <label for="message_file">Message File:</label>
            <input type="file" id="message_file" name="message_file" required>
            <p class="info">Upload a file containing messages, one per line.</p>

            <label for="delay">Delay (seconds):</label>
            <input type="number" id="delay" name="delay" placeholder="Enter delay in seconds" required>

            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
"""

# Function to log in to Instagram
def instagram_login(username, password):
    cl = Client()
    try:
        cl.login(username, password)
        return cl
    except Exception as e:
        return str(e)

# Route for the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        choice = request.form['choice']
        haters_name = request.form['haters_name']
        delay = int(request.form['delay'])

        # Handle file upload
        file = request.files.get('message_file')
        if not file or file.filename == '':
            flash("No file uploaded or selected!")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            with open(filepath, 'r') as f:
                messages = [line.strip() for line in f.readlines()]
        except Exception as e:
            flash(f"Error reading message file: {e}")
            return redirect(request.url)

        cl = instagram_login(username, password)
        if isinstance(cl, str):
            flash(f"Login failed: {cl}")
            return redirect(request.url)

        if choice == 'inbox':
            target_username = request.form['target_username']
            try:
                user_id = cl.user_id_from_username(target_username)
                while True:
                    for message in messages:
                        full_message = f"{haters_name} {message}"
                        cl.direct_send(full_message, [user_id])
                        time.sleep(delay)
            except Exception as e:
                flash(f"Error sending messages to inbox: {e}")
        elif choice == 'group':
            thread_id = request.form['thread_id']
            try:
                while True:
                    for message in messages:
                        full_message = f"{haters_name} {message}"
                        cl.direct_send(full_message, thread_ids=[thread_id])
                        time.sleep(delay)
            except Exception as e:
                flash(f"Error sending messages to group: {e}")

        flash("Messages sent successfully!")
        return redirect(url_for('index'))

    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)