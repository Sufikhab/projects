from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, string, random, os, qrcode

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB_NAME = 'urls.db'
QR_DIR = 'static/qrcodes'

os.makedirs(QR_DIR, exist_ok=True)

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT NOT NULL UNIQUE,
                clicks INTEGER DEFAULT 0
            )
        ''')

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    qr_path = None
    clicks = None

    if request.method == 'POST':
        original_url = request.form.get('url')
        if not original_url:
            flash('URL is required!')
            return redirect(url_for('index'))

        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        short_url = request.host_url + short_code

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)", (original_url, short_code))

        qr_img = qrcode.make(short_url)
        qr_file_path = os.path.join(QR_DIR, f"{short_code}.png")
        qr_img.save(qr_file_path)
        qr_path = '/' + qr_file_path

        clicks = 0

    return render_template('index.html', short_url=short_url, qr_path=qr_path, clicks=clicks)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT original_url, clicks FROM urls WHERE short_code = ?", (short_code,))
        result = cursor.fetchone()
        if result:
            original_url, clicks = result
            conn.execute("UPDATE urls SET clicks = ? WHERE short_code = ?", (clicks + 1, short_code))
            return redirect(original_url)
    return "Invalid short URL", 404

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8080)
