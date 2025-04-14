
from flask import Flask, request, jsonify, send_file, session, redirect, render_template
from flask_cors import CORS
from flask_session import Session
import csv, os, datetime, requests

app = Flask(__name__)
app.secret_key = 'donghwa_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
CORS(app)

ATTENDANCE_FILE = 'attendance.csv'
ADMIN_PASSWORD = 'admin123'

def send_kakao_alert(name, status, time):
    print(f"[샘플] 알림톡 전송 요청됨: {name}, {status}, {time}")
    # 실제 알림톡 연동 시 API 호출 구현

@app.route('/')
def home():
    return open('index.html', encoding='utf-8').read()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('password') == ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return jsonify({'message': 'logged out'})

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    name = data['name']
    status = data['status']
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(ATTENDANCE_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([name, now, status])
    send_kakao_alert(name, status, now)
    return jsonify({'success': True, 'name': name, 'status': status, 'time': now})

@app.route('/download')
def download():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    return send_file(ATTENDANCE_FILE, as_attachment=True)

@app.route('/live')
def live_list():
    people = {}
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, encoding='utf-8') as f:
            for row in csv.reader(f):
                if row[0] == 'Name': continue
                name, _, status = row
                people[name] = status
    live = [name for name, status in people.items() if status == '출근']
    return jsonify(live)

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/')
    records = []
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            records = list(reader)
    return render_template('dashboard.html', records=records)

if __name__ == '__main__':
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Check-in Time', 'Status'])
    app.run(host='0.0.0.0', port=5000)
