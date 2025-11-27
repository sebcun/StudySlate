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

def set_supabase_session():
    if 'access_token' in session and 'refresh_token' in session:
        supabase.auth.set_session(session['access_token'], session['refresh_token'])
        
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
            session['refresh_token'] = response.session.refresh_token
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

@app.route('/api/classes', methods=['GET'])
def get_classes():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    try:
        response = supabase.table('classes').select('*').eq('user_id', session['user_id']).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes/create', methods=['POST'])
def create_class():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    data = request.get_json()
    name = data.get('name')
    if not name or not name.strip():
        return jsonify({'error': 'Class name is required'}), 400
    try:
        response = supabase.table('classes').insert({'user_id': session['user_id'], 'name': name.strip()}).execute()
        
        return jsonify(response.data[0]), 201
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/class/<class_id>')
def class_page(class_id):
    if 'access_token' not in session:
        return redirect(url_for('login'))
    return render_template('class/class.html', class_id=class_id)
    
@app.route('/class/<class_id>/todo')
def class_todo_page(class_id):
    if 'access_token' not in session:
        return redirect(url_for('login'))
    return render_template('class/todo.html', class_id=class_id)

@app.route('/api/classes/<class_id>', methods=['GET'])
def get_class(class_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    try:
        response = supabase.table('classes').select('*').eq('id', class_id).eq('user_id', session['user_id']).execute()
        if response.data:
            return jsonify(response.data[0])
        else:
            return jsonify({'error': 'Class not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/classes/<class_id>/todos', methods=['GET'])
def get_todos(class_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    try:
        response = supabase.table('classes').select('id').eq('id', class_id).eq('user_id', session['user_id']).execute()
        if not response.data:
            return jsonify({'error': 'Class not found'}), 404
        todos_response = supabase.table('todos').select('*').eq('class_id', class_id).eq('user_id', session['user_id']).order('important', desc=True).order('created_at').execute()
        return jsonify(todos_response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes/<class_id>/todos', methods=['POST'])
def create_todo(class_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    data = request.get_json()
    text = data.get('text')
    if not text or not text.strip():
        return jsonify({'error': 'Todo text is required'}), 400
    try:
        response = supabase.table('classes').select('id').eq('id', class_id).eq('user_id', session['user_id']).execute()
        if not response.data:
            return jsonify({'error': 'Class not found'}), 404
        todo_response = supabase.table('todos').insert({'class_id': class_id, 'user_id': session['user_id'], 'text': text.strip(), 'done': False, 'important': False}).execute()
        return jsonify(todo_response.data[0]), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes/<class_id>/todos/<todo_id>', methods=['PUT'])
def update_todo(class_id, todo_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    data = request.get_json()
    updates = {}
    if 'done' in data:
        updates['done'] = data['done']
    if 'important' in data:
        updates['important'] = data['important']
    if not updates:
        return jsonify({'error': 'No updates provided'}), 400
    try:
        response = supabase.table('todos').update(updates).eq('id', todo_id).eq('class_id', class_id).eq('user_id', session['user_id']).execute()
        if response.data:
            return jsonify(response.data[0])
        else:
            return jsonify({'error': 'Todo not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes/<class_id>/todos/<todo_id>', methods=['DELETE'])
def delete_todo(class_id, todo_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    try:
        response = supabase.table('todos').delete().eq('id', todo_id).eq('class_id', class_id).eq('user_id', session['user_id']).execute()
        if response.data:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Todo not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/class/<class_id>/assignments')
def class_assignments_page(class_id):
    if 'access_token' not in session:
        return redirect(url_for('login'))
    return render_template('class/assignments.html', class_id=class_id)

@app.route('/api/classes/<class_id>/assignments', methods=['GET'])
def get_assignments(class_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    try:
        response = supabase.table('classes').select('id').eq('id', class_id).eq('user_id', session['user_id']).execute()
        if not response.data:
            return jsonify({'error': 'Class not found'}), 404
        assignments_response = supabase.table('assignments').select('*').eq('class_id', class_id).eq('user_id', session['user_id']).execute()
        return jsonify(assignments_response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes/<class_id>/assignments', methods=['POST'])
def create_assignment(class_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    data = request.get_json()
    text = data.get('text')
    due_date = data.get('due_date')
    if not text or not text.strip() or not due_date:
        return jsonify({'error': 'Assignment text and due date are required'}), 400
    try:
        response = supabase.table('classes').select('id').eq('id', class_id).eq('user_id', session['user_id']).execute()
        if not response.data:
            return jsonify({'error': 'Class not found'}), 404
        assignment_response = supabase.table('assignments').insert({'class_id': class_id, 'user_id': session['user_id'], 'text': text.strip(), 'due_date': due_date, 'done': False}).execute()
        return jsonify(assignment_response.data[0]), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes/<class_id>/assignments/<assignment_id>', methods=['PUT'])
def update_assignment(class_id, assignment_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    data = request.get_json()
    updates = {}
    if 'done' in data:
        updates['done'] = data['done']
        updates['updated_at'] = 'NOW()'
    if not updates:
        return jsonify({'error': 'No updates provided'}), 400
    try:
        response = supabase.table('assignments').update(updates).eq('id', assignment_id).eq('class_id', class_id).eq('user_id', session['user_id']).execute()
        if response.data:
            return jsonify(response.data[0])
        else:
            return jsonify({'error': 'Assignment not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes/<class_id>/assignments/<assignment_id>', methods=['DELETE'])
def delete_assignment(class_id, assignment_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    set_supabase_session()
    try:
        response = supabase.table('assignments').delete().eq('id', assignment_id).eq('class_id', class_id).eq('user_id', session['user_id']).execute()
        if response.data:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Assignment not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

                                                      
                                                                                    
@app.route('/class/<class_id>/lockin')
def class_lockin_page(class_id):
    if 'access_token' not in session:
        return redirect(url_for('login'))
    return render_template('class/lockin.html', class_id=class_id)

                                                      
                                                                                    
@app.route('/class/<class_id>/notebook')
def class_notebook_page(class_id):
    if 'access_token' not in session:
        return redirect(url_for('login'))
    return render_template('class/notebook.html', class_id=class_id)
                                                      

if __name__ == '__main__':
    app.run(debug=True)