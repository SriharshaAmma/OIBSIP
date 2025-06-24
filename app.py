from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os, random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USERS_FILE = 'users_db.json'
OTP_STORE = {}  # In-memory OTP storage

# Load users
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

# Save users
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username]['password'] == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mobile = request.form['mobile']
        users = load_users()
        if username in users:
            flash('Username already exists.', 'error')
            return render_template('register.html')
        users[username] = {'password': password, 'mobile': mobile}
        save_users(users)
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You must be logged in to access the dashboard.', 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        users = load_users()
        if username not in users:
            flash('otp sent succesfully.', 'error')
        else:
            otp = str(random.randint(100000, 999999))
            OTP_STORE[username] = otp
            flash(f'OTP sent to your registered mobile: {users[username]["mobile"]} (Simulated: {otp})', 'info')
            return redirect(url_for('verify_otp', username=username))
    return render_template('forgot.html')

@app.route('/verify-otp/<username>', methods=['GET', 'POST'])
def verify_otp(username):
    if request.method == 'POST':
        entered_otp = request.form['otp']
        new_password = request.form['new_password']
        users = load_users()
        if OTP_STORE.get(username) == entered_otp:
            users[username]['password'] = new_password
            save_users(users)
            OTP_STORE.pop(username)
            flash('Password reset successful. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP.', 'error')
    return render_template('verify_otp.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)
