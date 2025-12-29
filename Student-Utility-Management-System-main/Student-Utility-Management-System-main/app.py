from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB = 'database.db'

# ---------------- DB INIT -------------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Students
    cur.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT,
        semester TEXT,
        branch TEXT,
        password TEXT
    )''')

    # Notes
    cur.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY,
        content TEXT
    )''')

    # Tasks
    cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        content TEXT
    )''')

    # Class schedule
    cur.execute('''CREATE TABLE IF NOT EXISTS class_schedule (
        id INTEGER PRIMARY KEY,
        content TEXT
    )''')

    # Trash (only for deleted students)
    cur.execute('''CREATE TABLE IF NOT EXISTS trash (
        id INTEGER PRIMARY KEY,
        type TEXT,
        content TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES -------------------

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form['username']
    password = request.form['password']

    if name == 'admin' and password == 'admin':
        session['admin'] = True
        return redirect('/admin')

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT * FROM students WHERE name=? AND password=?', (name, password))
    student = cur.fetchone()
    conn.close()

    if student:
        session['student'] = name
        return redirect('/student_dashboard')
    return 'Invalid login'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- ADMIN DASHBOARD -------------------
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/')

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Students
    cur.execute('SELECT * FROM students')
    students = cur.fetchall()

    # Notes
    cur.execute('SELECT * FROM notes')
    notes = cur.fetchall()

    # Tasks
    cur.execute('SELECT * FROM tasks')
    tasks = cur.fetchall()

    # Class Schedule
    cur.execute('SELECT * FROM class_schedule')
    classes = cur.fetchall()

    # Trash (deleted students)
    cur.execute('SELECT * FROM trash')
    trash = cur.fetchall()

    conn.close()
    return render_template('admin_dashboard.html', students=students, notes=notes, tasks=tasks, classes=classes, trash=trash)

# ---------------- STUDENT MANAGEMENT -------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if not session.get('admin'):
        return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        semester = request.form['semester']
        branch = request.form['branch']
        password = request.form['password']
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute('INSERT INTO students (name, semester, branch, password) VALUES (?, ?, ?, ?)',
                    (name, semester, branch, password))
        conn.commit()
        conn.close()
        return redirect('/admin')
    return render_template('register_student.html')

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        semester = request.form['semester']
        branch = request.form['branch']
        password = request.form['password']
        cur.execute('UPDATE students SET name=?, semester=?, branch=?, password=? WHERE id=?',
                    (name, semester, branch, password, id))
        conn.commit()
        conn.close()
        return redirect('/admin')
    cur.execute('SELECT * FROM students WHERE id=?', (id,))
    student = cur.fetchone()
    conn.close()
    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<int:id>')
def delete_student(id):
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT name, semester, branch, password FROM students WHERE id=?', (id,))
    student = cur.fetchone()
    if student:
        student_str = f"{student[0]}|{student[1]}|{student[2]}|{student[3]}"
        cur.execute('INSERT INTO trash (type, content) VALUES (?, ?)', ('student', student_str))
        cur.execute('DELETE FROM students WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')
# ---------------- NOTES -------------------
@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    if request.method == 'POST':
        note = request.form['note']
        cur.execute('INSERT INTO notes (content) VALUES (?)', (note,))
        conn.commit()
    cur.execute('SELECT * FROM notes')
    notes = cur.fetchall()
    conn.close()
    return render_template('manage_notes.html', notes=notes)

@app.route('/delete_note/<int:id>')
def delete_note(id):
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT content FROM notes WHERE id=?', (id,))
    note = cur.fetchone()
    if note:
        cur.execute('INSERT INTO trash (type, content) VALUES (?, ?)', ('note', note[0]))
        cur.execute('DELETE FROM notes WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/notes')

# ---------------- TASKS -------------------
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    if request.method == 'POST':
        task = request.form['task']
        cur.execute('INSERT INTO tasks (content) VALUES (?)', (task,))
        conn.commit()
    cur.execute('SELECT * FROM tasks')
    tasks = cur.fetchall()
    conn.close()
    return render_template('manage_tasks.html', tasks=tasks)

@app.route('/delete_task/<int:id>')
def delete_task(id):
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT content FROM tasks WHERE id=?', (id,))
    task = cur.fetchone()
    if task:
        cur.execute('INSERT INTO trash (type, content) VALUES (?, ?)', ('task', task[0]))
        cur.execute('DELETE FROM tasks WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/tasks')


# ---------------- CLASS SCHEDULE -------------------
@app.route('/class_schedule', methods=['GET', 'POST'])
def class_schedule():
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    if request.method == 'POST':
        schedule = request.form['schedule']
        cur.execute('INSERT INTO class_schedule (content) VALUES (?)', (schedule,))
        conn.commit()
    cur.execute('SELECT * FROM class_schedule')
    classes = cur.fetchall()
    conn.close()
    return render_template('manage_classes.html', classes=classes)

@app.route('/delete_class/<int:id>')
def delete_class(id):
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT content FROM class_schedule WHERE id=?', (id,))
    cls = cur.fetchone()
    if cls:
        cur.execute('INSERT INTO trash (type, content) VALUES (?, ?)', ('class', cls[0]))
        cur.execute('DELETE FROM class_schedule WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/class_schedule')

# ---------------- TRASH -------------------
@app.route('/trash')
def trash():
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT * FROM trash')
    trash = cur.fetchall()
    conn.close()
    return render_template('trash.html', trash=trash)

@app.route('/restore/<int:id>')
def restore(id):
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT * FROM trash WHERE id=?', (id,))
    t = cur.fetchone()
    if t and t[1] == 'student':
        parts = t[2].split('|')
        if len(parts) == 4:
            cur.execute('INSERT INTO students (name, semester, branch, password) VALUES (?, ?, ?, ?)',
                        (parts[0], parts[1], parts[2], parts[3]))
        cur.execute('DELETE FROM trash WHERE id=?', (id,))
        conn.commit()
    conn.close()
    return redirect('/trash')

@app.route('/permanent_delete/<int:id>')
def permanent_delete(id):
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('DELETE FROM trash WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/trash')

# ---------------- STUDENT DASHBOARD -------------------
@app.route('/student_dashboard')
def student_dashboard():
    if not session.get('student'):
        return redirect('/')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT * FROM notes')
    notes = cur.fetchall()
    cur.execute('SELECT * FROM tasks')
    tasks = cur.fetchall()
    cur.execute('SELECT * FROM class_schedule')
    classes = cur.fetchall()
    conn.close()
    return render_template('student_dashboard.html', notes=notes, tasks=tasks, classes=classes)

# ---------------- MAIN -------------------
if __name__ == '__main__':
    app.run(debug=True)
