import sqlite3
import hashlib
import time
from flask import Flask, request, redirect, jsonify, abort

app = Flask(__name__)

DATABASE = 'database.db'
BASE_URL = 'http://127.0.0.1:5000/'


# initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_url TEXT NOT NULL UNIQUE,
                creation_timestamp INTEGER NOT NULL,
                expiration_timestamp INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_url TEXT NOT NULL,
                access_timestamp INTEGER NOT NULL,
                ip_address TEXT NOT NULL
            );
        ''')


# Generate a hash-based short URL
def generate_short_url(original_url):
    return hashlib.md5(original_url.encode()).hexdigest()[:6]


# Save URL and metadata to the database
def save_url(original_url, short_url, expiry_hours):
    creation_time = int(time.time())
    expiry_time = creation_time + expiry_hours * 3600

    with sqlite3.connect(DATABASE) as conn:
        try:
            conn.execute('''
                INSERT INTO urls (original_url, short_url, creation_timestamp, expiration_timestamp)
                VALUES (?, ?, ?, ?)
            ''', (original_url, short_url, creation_time, expiry_time))
        except sqlite3.IntegrityError:
            pass  # iignore if the short URL already exists


# Fetch URL metadata from the database
def get_url_metadata(short_url):
    with sqlite3.connect(DATABASE) as conn:
        return conn.execute('''
            SELECT original_url, expiration_timestamp
            FROM urls WHERE short_url = ?
        ''', (short_url,)).fetchone()


# Log access details in the database
def log_access(short_url, ip_address):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            INSERT INTO access_logs (short_url, access_timestamp, ip_address)
            VALUES (?, ?, ?)
        ''', (short_url, int(time.time()), ip_address))


# Fetch analytics for a specific shortened URL
def get_analytics_data(short_url):
    with sqlite3.connect(DATABASE) as conn:
        logs = conn.execute('''
            SELECT access_timestamp, ip_address FROM access_logs WHERE short_url = ?
        ''', (short_url,)).fetchall()

        url_data = conn.execute('''
            SELECT original_url, creation_timestamp, expiration_timestamp
            FROM urls WHERE short_url = ?
        ''', (short_url,)).fetchone()

    return url_data, logs


@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('url')
    expiry_hours = data.get('expiry', 24)

    if not original_url or not original_url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid or missing URL'}), 400

    short_url = generate_short_url(original_url)
    save_url(original_url, short_url, expiry_hours)

    return jsonify({'short_url': BASE_URL + short_url}), 201


@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    metadata = get_url_metadata(short_url)
    if not metadata:
        abort(404, 'URL not found')

    original_url, expiration_time = metadata
    if int(time.time()) > expiration_time:
        abort(410, 'URL has expired')

    log_access(short_url, request.remote_addr)
    return redirect(original_url)


@app.route('/analytics/<short_url>', methods=['GET'])
def analytics(short_url):
    url_data, logs = get_analytics_data(short_url)
    if not url_data:
        abort(404, 'URL not found')

    original_url, creation_time, expiration_time = url_data

    return jsonify({
        'original_url': original_url,
        'creation_timestamp': creation_time,
        'expiration_timestamp': expiration_time,
        'access_logs': [{'timestamp': log[0], 'ip_address': log[1]} for log in logs]
    })


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
