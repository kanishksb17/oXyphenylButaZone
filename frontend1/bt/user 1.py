from flask import Flask, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change for production!

# In-memory user store: {email: {username, password_hash}}
users = {}

def get_current_user():
    email = session.get('user_email')
    return users.get(email)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not (email and username and password):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    if email in users:
        return jsonify({'success': False, 'error': 'Email already registered'}), 409
    users[email] = {
        'username': username,
        'password_hash': generate_password_hash(password)
    }
    session['user_email'] = email
    return jsonify({'success': True, 'message': 'Registered', 'username': username})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    user = users.get(email)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    session['user_email'] = email
    return jsonify({'success': True, 'message': 'Logged in', 'username': user['username']})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_email', None)
    return jsonify({'success': True, 'message': 'Logged out'})

@app.route('/api/profile', methods=['GET', 'POST'])
def profile():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    if request.method == 'POST':
        data = request.get_json()
        new_username = data.get('username', '').strip()
        if new_username:
            user['username'] = new_username
            return jsonify({'success': True, 'message': 'Username updated', 'username': new_username})
        else:
            return jsonify({'success': False, 'error': 'Username required'}), 400
    return jsonify({'success': True, 'username': user['username']})

@app.route('/api/password', methods=['POST'])
def change_password():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    data = request.get_json()
    old_pw = data.get('old_password', '')
    new_pw = data.get('new_password', '')
    if not check_password_hash(user['password_hash'], old_pw):
        return jsonify({'success': False, 'error': 'Current password incorrect'}), 403
    if not new_pw:
        return jsonify({'success': False, 'error': 'New password required'}), 400
    user['password_hash'] = generate_password_hash(new_pw)
    return jsonify({'success': True, 'message': 'Password changed'})

if __name__ == '__main__':
    app.run(debug=True)