from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.route('/')
def home():
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pass
    return render_template('login.html')

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')
    try:
        response = supabase.auth.sign_in_with_otp({
            'email': email,
            'options': {
                'should_create_user': True,
            },
        })
        print(response)
        if response:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to send code'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    try:
        response = supabase.auth.verify_otp({'email': email, 'token': code, 'type': 'email'})
        if response.session:
            session['access_token'] = response.session.access_token
            session['user_id'] = response.user.id
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid code'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)