from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                priority TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        ''')
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status', 'all')
    priority = request.args.get('priority', 'all')
    db = get_db_connection()
    query = 'SELECT * FROM tasks'
    conditions = []

    if status != 'all':
        conditions.append(f"completed = {1 if status == 'completed' else 0}")
    if priority != 'all':
        conditions.append(f"priority = '{priority}'")

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    tasks = db.execute(query).fetchall()
    db.close()
    return jsonify([dict(task) for task in tasks])

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    task_text = data.get('task', '')
    priority = data.get('priority', 'medium')
    if task_text:
        db = get_db_connection()
        db.execute('INSERT INTO tasks (text, priority) VALUES (?, ?)', (task_text, priority))
        db.commit()
        db.close()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'error': 'Task text is required'}), 400

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    data = request.get_json()
    completed = data.get('completed', False)
    db = get_db_connection()
    db.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))
    db.commit()
    db.close()
    return jsonify({'success': True})

@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    data = request.json
    task_text = data.get('task', '')
    if task_text:
        db = get_db_connection()
        db.execute('UPDATE tasks SET text = ? WHERE id = ?', (task_text, task_id))
        db.commit()
        db.close()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'error': 'Task text is required'}), 400

@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db = get_db_connection()
    db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    db.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
