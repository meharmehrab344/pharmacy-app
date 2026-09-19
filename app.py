from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'mehar_pharmaceuticals_secret_key'

def init_db():
    conn = sqlite3.connect('pharmaceuticals.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('pharmaceuticals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock FROM medicines WHERE user_id = ?", (session['user_id'],))
    medicines = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', medicines=medicines, username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('pharmaceuticals.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid Username or Password! <a href='/login'>Try Again</a>"
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        key = request.form['license_key']
        
        if key != "MEHAR-2026-WARIS":
            return "Invalid License Key! <a href='/register'>Try Again</a>"
            
        try:
            conn = sqlite3.connect('pharmaceuticals.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists! <a href='/register'>Choose another</a>"
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_medicine():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    price = float(request.form['price'])
    stock = int(request.form['stock'])

    conn = sqlite3.connect('pharmaceuticals.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO medicines (user_id, name, price, stock) VALUES (?, ?, ?, ?)",
                   (session['user_id'], name, price, stock))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/sell', methods=['POST'])
def sell_medicine():
    if 'user_id' not in session:
        return jsonify({'success': False})
        
    data = request.get_json()
    items = data.get('items', [])

    conn = sqlite3.connect('pharmaceuticals.db')
    cursor = conn.cursor()

    for item in items:
        med_id = item['id']
        qty = item['qty']
        cursor.execute("UPDATE medicines SET stock = stock - ? WHERE id = ? AND user_id = ?",
                       (qty, med_id, session['user_id']))

    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
