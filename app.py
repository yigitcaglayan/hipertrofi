from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
import functools

app = Flask(__name__)
app.secret_key = 'musclefit_secret_key_secure_123' # Guvenlik icin secret key

# Veritabanı bağlantısı
import os

def get_db_connection():
    # Absolute path kullanıyoruz ki PythonAnywhere'de sorun çıkmasın
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'muscle_trainer.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Veritabanı oluşturma
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Favorites tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (exercise_id) REFERENCES exercises (id),
            UNIQUE(user_id, exercise_id)
        )
    ''')
    
    # Kas grupları tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS muscle_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            turkish_name TEXT NOT NULL,
            coordinates TEXT NOT NULL,
            side TEXT NOT NULL
        )
    ''')
    
    # Egzersizler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            muscle_id INTEGER,
            name TEXT NOT NULL,
            turkish_name TEXT NOT NULL,
            description TEXT,
            difficulty TEXT,
            equipment TEXT,
            sets TEXT,
            reps TEXT,
            FOREIGN KEY (muscle_id) REFERENCES muscle_groups (id)
        )
    ''')
    
    # Varsayılan verileri ekle
    cursor.execute('SELECT COUNT(*) FROM muscle_groups')
    if cursor.fetchone()[0] == 0:
        # Ön görünüm kasları
        muscle_data = [
            # Göğüs
            (1, 'Chest', 'Göğüs', json.dumps({'x': 250, 'y': 180, 'width': 100, 'height': 80}), 'front'),
            # Ön kol (biceps)
            (2, 'Biceps', 'Ön Kol (Biceps)', json.dumps({'x': 150, 'y': 200, 'width': 50, 'height': 80}), 'front'),
            (3, 'Biceps', 'Ön Kol (Biceps)', json.dumps({'x': 400, 'y': 200, 'width': 50, 'height': 80}), 'front'),
            # Karın
            (4, 'Abs', 'Karın', json.dumps({'x': 250, 'y': 280, 'width': 100, 'height': 120}), 'front'),
            # Ön bacak (quadriceps)
            (5, 'Quadriceps', 'Ön Bacak', json.dumps({'x': 200, 'y': 450, 'width': 60, 'height': 150}), 'front'),
            (6, 'Quadriceps', 'Ön Bacak', json.dumps({'x': 340, 'y': 450, 'width': 60, 'height': 150}), 'front'),
            # Omuz
            (7, 'Shoulders', 'Omuz', json.dumps({'x': 180, 'y': 140, 'width': 60, 'height': 50}), 'front'),
            (8, 'Shoulders', 'Omuz', json.dumps({'x': 360, 'y': 140, 'width': 60, 'height': 50}), 'front'),
            
            # Arka görünüm kasları
            # Sırt (lat)
            (9, 'Back', 'Sırt', json.dumps({'x': 220, 'y': 180, 'width': 160, 'height': 120}), 'back'),
            # Arka kol (triceps)
            (10, 'Triceps', 'Arka Kol (Triceps)', json.dumps({'x': 150, 'y': 200, 'width': 50, 'height': 80}), 'back'),
            (11, 'Triceps', 'Arka Kol (Triceps)', json.dumps({'x': 400, 'y': 200, 'width': 50, 'height': 80}), 'back'),
            # Kalça
            (12, 'Glutes', 'Kalça', json.dumps({'x': 220, 'y': 320, 'width': 160, 'height': 100}), 'back'),
            # Arka bacak (hamstring)
            (13, 'Hamstrings', 'Arka Bacak', json.dumps({'x': 200, 'y': 450, 'width': 60, 'height': 150}), 'back'),
            (14, 'Hamstrings', 'Arka Bacak', json.dumps({'x': 340, 'y': 450, 'width': 60, 'height': 150}), 'back'),
            # Baldır
            (15, 'Calves', 'Baldır', json.dumps({'x': 210, 'y': 600, 'width': 50, 'height': 80}), 'back'),
            (16, 'Calves', 'Baldır', json.dumps({'x': 340, 'y': 600, 'width': 50, 'height': 80}), 'back'),
        ]
        
        cursor.executemany('''
            INSERT INTO muscle_groups (id, name, turkish_name, coordinates, side)
            VALUES (?, ?, ?, ?, ?)
        ''', muscle_data)
        
        # Egzersizler
        exercise_data = [
            # Göğüs egzersizleri
            (1, 'Bench Press', 'Bench Press', 'Göğüs kaslarını geliştirmek için en etkili hareket. Yatay pozisyonda bar ile yapılır.', 'Orta', 'Barbell', '3-4 set', '8-12 tekrar'),
            (1, 'Dumbbell Flyes', 'Dumbbell Flyes', 'Göğüs kaslarını germe hareketi ile çalıştırır.', 'Orta', 'Dumbbell', '3 set', '10-12 tekrar'),
            (1, 'Push-ups', 'Şınav', 'Kendi vücut ağırlığınızla yapabileceğiniz temel göğüs hareketi.', 'Başlangıç', 'Vücut Ağırlığı', '3-4 set', '10-20 tekrar'),
            (1, 'Incline Dumbbell Press', 'İncline Dumbbell Press', 'Üst göğüs kaslarını hedefler.', 'Orta', 'Dumbbell', '3-4 set', '8-12 tekrar'),
            (1, 'Cable Flyes', 'Kablo Flyes', 'Göğüs kaslarını izole ederek çalışmaya olanak sağlar.', 'İleri', 'Kablo', '3 set', '12-15 tekrar'),
            
            # Biceps egzersizleri
            (2, 'Barbell Curl', 'Barbell Curl', 'Biceps kaslarını geliştirmek için klasik hareket.', 'Başlangıç', 'Barbell', '3 set', '10-12 tekrar'),
            (2, 'Hammer Curl', 'Çekiç Curl', 'Önkol ve biceps kaslarını birlikte çalıştırır.', 'Orta', 'Dumbbell', '3 set', '10-15 tekrar'),
            (2, 'Concentration Curl', 'Concentration Curl', 'Biceps kaslarını izole ederek çalıştırır.', 'Orta', 'Dumbbell', '3 set', '10-12 tekrar'),
            (2, 'Preacher Curl', 'Preacher Curl', 'Biceps kaslarını izole ederek maksimum kontraksiyon sağlar.', 'İleri', 'EZ Bar', '3-4 set', '8-12 tekrar'),
            (2, 'Cable Curl', 'Kablo Curl', 'Sabit gerilim ile biceps çalıştırır.', 'Orta', 'Kablo', '3 set', '12-15 tekrar'),
            (3, 'Barbell Curl', 'Barbell Curl', 'Biceps kaslarını geliştirmek için klasik hareket.', 'Başlangıç', 'Barbell', '3 set', '10-12 tekrar'),
            (3, 'Hammer Curl', 'Çekiç Curl', 'Önkol ve biceps kaslarını birlikte çalıştırır.', 'Orta', 'Dumbbell', '3 set', '10-15 tekrar'),
            (3, 'Concentration Curl', 'Concentration Curl', 'Biceps kaslarını izole ederek çalıştırır.', 'Orta', 'Dumbbell', '3 set', '10-12 tekrar'),
            (3, 'Preacher Curl', 'Preacher Curl', 'Biceps kaslarını izole ederek maksimum kontraksiyon sağlar.', 'İleri', 'EZ Bar', '3-4 set', '8-12 tekrar'),
            (3, 'Cable Curl', 'Kablo Curl', 'Sabit gerilim ile biceps çalıştırır.', 'Orta', 'Kablo', '3 set', '12-15 tekrar'),
            
            # Karın egzersizleri
            (4, 'Crunches', 'Mekik', 'Karın kaslarını çalıştırmak için temel hareket.', 'Başlangıç', 'Vücut Ağırlığı', '3 set', '15-25 tekrar'),
            (4, 'Plank', 'Plank', 'Core kaslarını güçlendiren statik egzersiz.', 'Orta', 'Vücut Ağırlığı', '3 set', '30-60 saniye'),
            (4, 'Leg Raises', 'Bacak Kaldırma', 'Alt karın kaslarını hedefler.', 'Orta', 'Vücut Ağırlığı', '3 set', '12-15 tekrar'),
            (4, 'Bicycle Crunches', 'Bisiklet Mekik', 'Yan karın kaslarını çalıştırır.', 'Orta', 'Vücut Ağırlığı', '3 set', '15-20 tekrar'),
            (4, 'Mountain Climbers', 'Dağcı', 'Dinamik core hareketi.', 'Orta', 'Vücut Ağırlığı', '3 set', '20-30 tekrar'),
            
            # Quadriceps egzersizleri
            (5, 'Squats', 'Squat', 'Bacak kaslarını geliştirmek için en temel ve etkili hareket.', 'Orta', 'Barbell', '4 set', '8-12 tekrar'),
            (5, 'Leg Press', 'Leg Press', 'Makinede bacak kaslarını güvenli bir şekilde çalıştırır.', 'Başlangıç', 'Makine', '3-4 set', '10-15 tekrar'),
            (5, 'Lunges', 'Lunge', 'Tek bacakla yapılan denge ve kuvvet hareketi.', 'Orta', 'Dumbbell', '3 set', '10-12 tekrar (her bacak)'),
            (5, 'Leg Extension', 'Leg Extension', 'Quadriceps kaslarını izole eder.', 'Başlangıç', 'Makine', '3 set', '12-15 tekrar'),
            (5, 'Bulgarian Split Squat', 'Bulgarian Split Squat', 'Tek bacak squat varyasyonu.', 'İleri', 'Dumbbell', '3 set', '8-12 tekrar (her bacak)'),
            (6, 'Squats', 'Squat', 'Bacak kaslarını geliştirmek için en temel ve etkili hareket.', 'Orta', 'Barbell', '4 set', '8-12 tekrar'),
            (6, 'Leg Press', 'Leg Press', 'Makinede bacak kaslarını güvenli bir şekilde çalıştırır.', 'Başlangıç', 'Makine', '3-4 set', '10-15 tekrar'),
            (6, 'Lunges', 'Lunge', 'Tek bacakla yapılan denge ve kuvvet hareketi.', 'Orta', 'Dumbbell', '3 set', '10-12 tekrar (her bacak)'),
            (6, 'Leg Extension', 'Leg Extension', 'Quadriceps kaslarını izole eder.', 'Başlangıç', 'Makine', '3 set', '12-15 tekrar'),
            (6, 'Bulgarian Split Squat', 'Bulgarian Split Squat', 'Tek bacak squat varyasyonu.', 'İleri', 'Dumbbell', '3 set', '8-12 tekrar (her bacak)'),
            
            # Omuz egzersizleri
            (7, 'Overhead Press', 'Shoulder Press', 'Omuz kaslarını geliştirmek için temel hareket.', 'Orta', 'Barbell', '3-4 set', '8-12 tekrar'),
            (7, 'Lateral Raises', 'Lateral Raise', 'Omuz yan kaslarını izole eder.', 'Başlangıç', 'Dumbbell', '3 set', '12-15 tekrar'),
            (7, 'Front Raises', 'Front Raise', 'Ön omuz kaslarını çalıştırır.', 'Başlangıç', 'Dumbbell', '3 set', '12-15 tekrar'),
            (7, 'Rear Delt Flyes', 'Peck Deck Fly', 'Arka deltoid kaslarını izole eder.', 'Orta', 'Dumbbell', '3 set', '12-15 tekrar'),
            (7, 'Upright Row', 'Upright Row', 'Omuz ve trapez kaslarını çalıştırır.', 'Orta', 'Barbell', '3 set', '10-12 tekrar'),
            (8, 'Overhead Press', 'Shoulder Press', 'Omuz kaslarını geliştirmek için temel hareket.', 'Orta', 'Barbell', '3-4 set', '8-12 tekrar'),
            (8, 'Lateral Raises', 'Lateral Raise', 'Omuz yan kaslarını izole eder.', 'Başlangıç', 'Dumbbell', '3 set', '12-15 tekrar'),
            (8, 'Front Raises', 'Front Raise', 'Ön omuz kaslarını çalıştırır.', 'Başlangıç', 'Dumbbell', '3 set', '12-15 tekrar'),
            (8, 'Rear Delt Flyes', 'Peck Deck Fly', 'Arka deltoid kaslarını izole eder.', 'Orta', 'Dumbbell', '3 set', '12-15 tekrar'),
            (8, 'Upright Row', 'Upright Row', 'Omuz ve trapez kaslarını çalıştırır.', 'Orta', 'Barbell', '3 set', '10-12 tekrar'),
            
            # Sırt egzersizleri
            (9, 'Pull-ups', 'Barfiks', 'Sırt kaslarını geliştirmek için en etkili vücut ağırlığı hareketi.', 'Orta', 'Barfiks Barı', '3-4 set', '6-12 tekrar'),
            (9, 'Barbell Rows', 'Barbell Row', 'Sırt kalınlığını artıran temel hareket.', 'Orta', 'Barbell', '3-4 set', '8-12 tekrar'),
            (9, 'Deadlifts', 'Deadlift', 'Tüm vücut kaslarını çalıştıran compound hareket.', 'İleri', 'Barbell', '3-4 set', '5-8 tekrar'),
            (9, 'Lat Pulldown', 'Lat Pulldown', 'Sırt genişliğini artırır.', 'Başlangıç', 'Makine', '3 set', '10-12 tekrar'),
            (9, 'T-Bar Row', 'T-Bar Row', 'Sırt kalınlığı için etkili hareket.', 'Orta', 'T-Bar', '3 set', '8-12 tekrar'),
            
            # Triceps egzersizleri
            (10, 'Tricep Dips', 'Tricep Dips', 'Arka kol kaslarını geliştirmek için etkili hareket.', 'Orta', 'Paralel Bar', '3 set', '8-15 tekrar'),
            (10, 'Rope Pushdown', 'Cable Rope Pushdown', 'Kablo ile triceps kaslarını çalıştırır.', 'Başlangıç', 'Kablo', '3 set', '12-15 tekrar'),
            (10, 'Skull Crushers', 'Skull Crusher', 'Triceps kaslarını izole eden hareket.', 'İleri', 'EZ Bar', '3 set', '10-12 tekrar'),
            (10, 'Close-Grip Bench', 'Dar Tutuş Bench', 'Triceps kütlesi için compound hareket.', 'Orta', 'Barbell', '3-4 set', '8-12 tekrar'),
            (10, 'Overhead Extension', 'Overhead Extension', 'Triceps uzun başını hedefler.', 'Orta', 'Dumbbell', '3 set', '10-12 tekrar'),
            (11, 'Tricep Dips', 'Tricep Dips', 'Arka kol kaslarını geliştirmek için etkili hareket.', 'Orta', 'Paralel Bar', '3 set', '8-15 tekrar'),
            (11, 'Rope Pushdown', 'Cable Rope Pushdown', 'Kablo ile triceps kaslarını çalıştırır.', 'Başlangıç', 'Kablo', '3 set', '12-15 tekrar'),
            (11, 'Skull Crushers', 'Skull Crusher', 'Triceps kaslarını izole eden hareket.', 'İleri', 'EZ Bar', '3 set', '10-12 tekrar'),
            (11, 'Close-Grip Bench', 'Dar Tutuş Bench', 'Triceps kütlesi için compound hareket.', 'Orta', 'Barbell', '3-4 set', '8-12 tekrar'),
            (11, 'Overhead Extension', 'Overhead Extension', 'Triceps uzun başını hedefler.', 'Orta', 'Dumbbell', '3 set', '10-12 tekrar'),
            
            # Kalça egzersizleri
            (12, 'Hip Thrusts', 'Hip Thrust', 'Kalça kaslarını maksimum aktivasyonla çalıştırır.', 'Orta', 'Barbell', '3-4 set', '10-15 tekrar'),
            (12, 'Glute Bridges', 'Hip Bridge', 'Kalça kaslarını izole eden başlangıç hareketi.', 'Başlangıç', 'Vücut Ağırlığı', '3 set', '15-20 tekrar'),
            (12, 'Bulgarian Split Squats', 'Bulgarian Split Squat', 'Tek bacakla yapılan ileri seviye hareket.', 'İleri', 'Dumbbell', '3 set', '8-12 tekrar (her bacak)'),
            (12, 'Cable Kickbacks', 'Cable Kickback', 'Kalça kaslarını izole eder.', 'Başlangıç', 'Kablo', '3 set', '12-15 tekrar (her bacak)'),
            (12, 'Sumo Deadlift', 'Sumo Deadlift', 'Kalça ve iç bacak kaslarını çalıştırır.', 'Orta', 'Barbell', '3-4 set', '8-12 tekrar'),
            
            # Hamstring egzersizleri
            (13, 'Romanian Deadlifts', 'Romanian Deadlift', 'Arka bacak kaslarını hedef alan deadlift varyasyonu.', 'Orta', 'Barbell', '3-4 set', '8-12 tekrar'),
            (13, 'Leg Curls', 'Leg Curl', 'Makinede hamstring kaslarını izole eder.', 'Başlangıç', 'Makine', '3 set', '12-15 tekrar'),
            (13, 'Good Mornings', 'Good Morning', 'Arka bacak ve sırt kaslarını birlikte çalıştırır.', 'İleri', 'Barbell', '3 set', '10-12 tekrar'),
            (13, 'Nordic Curls', 'Nordic Curl', 'İleri seviye hamstring hareketi.', 'İleri', 'Vücut Ağırlığı', '3 set', '5-8 tekrar'),
            (13, 'Stiff-Leg Deadlift', 'Stiff-Leg Deadlift', 'Hamstring esnekliği ve kuvveti geliştirir.', 'Orta', 'Barbell', '3 set', '10-12 tekrar'),
            (14, 'Romanian Deadlifts', 'Romanian Deadlift', 'Arka bacak kaslarını hedef alan deadlift varyasyonu.', 'Orta', 'Barbell', '3-4 set', '8-12 tekrar'),
            (14, 'Leg Curls', 'Leg Curl', 'Makinede hamstring kaslarını izole eder.', 'Başlangıç', 'Makine', '3 set', '12-15 tekrar'),
            (14, 'Good Mornings', 'Good Morning', 'Arka bacak ve sırt kaslarını birlikte çalıştırır.', 'İleri', 'Barbell', '3 set', '10-12 tekrar'),
            (14, 'Nordic Curls', 'Nordic Curl', 'İleri seviye hamstring hareketi.', 'İleri', 'Vücut Ağırlığı', '3 set', '5-8 tekrar'),
            (14, 'Stiff-Leg Deadlift', 'Stiff-Leg Deadlift', 'Hamstring esnekliği ve kuvveti geliştirir.', 'Orta', 'Barbell', '3 set', '10-12 tekrar'),
            
            # Baldır egzersizleri
            (15, 'Calf Raises', 'Baldır Kaldırma', 'Ayakta baldır kaslarını çalıştırır.', 'Başlangıç', 'Vücut Ağırlığı', '3-4 set', '15-20 tekrar'),
            (15, 'Seated Calf Raises', 'Oturarak Baldır', 'Oturarak baldır kaslarını izole eder.', 'Orta', 'Makine', '3 set', '12-15 tekrar'),
            (15, 'Jump Rope', 'İp Atlama', 'Kardiyoyla birlikte baldır kaslarını güçlendirir.', 'Başlangıç', 'İp', '3-5 set', '30-60 saniye'),
            (15, 'Donkey Calf Raises', 'Donkey Calf Raise', 'Maksimum baldır gerilimi sağlar.', 'Orta', 'Makine', '3 set', '12-15 tekrar'),
            (15, 'Box Jumps', 'Box Jump', 'Patlayıcı güç ve baldır kuvveti geliştirir.', 'Orta', 'Box', '3 set', '8-12 tekrar'),
            (16, 'Calf Raises', 'Baldır Kaldırma', 'Ayakta baldır kaslarını çalıştırır.', 'Başlangıç', 'Vücut Ağırlığı', '3-4 set', '15-20 tekrar'),
            (16, 'Seated Calf Raises', 'Oturarak Baldır', 'Oturarak baldır kaslarını izole eder.', 'Orta', 'Makine', '3 set', '12-15 tekrar'),
            (16, 'Jump Rope', 'İp Atlama', 'Kardiyoyla birlikte baldır kaslarını güçlendirir.', 'Başlangıç', 'İp', '3-5 set', '30-60 saniye'),
            (16, 'Donkey Calf Raises', 'Donkey Calf Raise', 'Maksimum baldır gerilimi sağlar.', 'Orta', 'Makine', '3 set', '12-15 tekrar'),
            (16, 'Box Jumps', 'Box Jump', 'Patlayıcı güç ve baldır kuvveti geliştirir.', 'Orta', 'Box', '3 set', '8-12 tekrar'),
        ]
        
        cursor.executemany('''
            INSERT INTO exercises (muscle_id, name, turkish_name, description, difficulty, equipment, sets, reps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', exercise_data)
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/muscles')
def get_muscles():
    conn = get_db_connection()
    muscles = conn.execute('SELECT * FROM muscle_groups').fetchall()
    conn.close()
    return jsonify([dict(m) for m in muscles])

@app.route('/api/exercises/<int:muscle_id>')
def get_exercises(muscle_id):
    conn = get_db_connection()
    exercises = conn.execute(
        'SELECT * FROM exercises WHERE muscle_id = ? LIMIT 5',
        (muscle_id,)
    ).fetchall()
    conn.close()
    
    # Add image URLs to exercises
    exercise_list = []
    base_url = "/static/images/exercises/"
    
    # Muscle ID to English Name mapping for file naming convention
    muscle_map = {
        1: "chest", 2: "biceps", 3: "biceps",
        4: "abs",
        5: "quadriceps", 6: "quadriceps",
        7: "shoulders", 8: "shoulders",
        9: "back",
        10: "triceps", 11: "triceps",
        12: "glutes",
        13: "hamstrings", 14: "hamstrings",
        15: "calves", 16: "calves"
    }
    
    for i, ex in enumerate(exercises):
        ex_dict = dict(ex)
        muscle_name = muscle_map.get(muscle_id, "unknown")
        # exercise_1, exercise_2, etc. (1-indexed based on their order in DB for that muscle)
        ex_dict['image_url'] = f"{base_url}{muscle_name}_exercise_{i+1}.png"
        
        # Check if favorite (if logged in)
        ex_dict['is_favorite'] = False
        if 'user_id' in session:
            conn = get_db_connection()
            fav = conn.execute('SELECT id FROM favorites WHERE user_id = ? AND exercise_id = ?', 
                             (session['user_id'], ex['id'])).fetchone()
            conn.close()
            if fav:
                ex_dict['is_favorite'] = True
                
        exercise_list.append(ex_dict)
        
    return jsonify(exercise_list)

# Auth Decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized', 'message': 'Lütfen giriş yapın'}), 401
        return view(**kwargs)
    return wrapped_view

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Tüm alanları doldurun'}), 400
        
    hashed_pw = generate_password_hash(password)
    
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                     (username, email, hashed_pw))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Kayıt başarılı! Giriş yapabilirsiniz.'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Kullanıcı adı veya email zaten kayıtlı!'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    identifier = data.get('identifier') # Username or Email
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (identifier, identifier)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'success': True, 'username': user['username']})
    
    return jsonify({'success': False, 'message': 'Hatalı kullanıcı adı veya şifre!'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check_auth')
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'username': session['username']})
    return jsonify({'authenticated': False})

@app.route('/api/favorites', methods=['GET', 'POST', 'DELETE'])
@login_required
def favorites():
    conn = get_db_connection()
    user_id = session['user_id']
    
    if request.method == 'GET':
        favs = conn.execute('''
            SELECT f.id as fav_id, e.* 
            FROM favorites f
            JOIN exercises e ON f.exercise_id = e.id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        ''', (user_id,)).fetchall()
        conn.close()
        
        # Image mapping logic needs to be replicated or simplified here
        # Since we just need the list, we might implement image logic similar to get_exercises later or simplify
        exercises = [dict(f) for f in favs]
        return jsonify(exercises)
        
    if request.method == 'POST':
        data = request.json
        exercise_id = data.get('exercise_id')
        try:
            conn.execute('INSERT INTO favorites (user_id, exercise_id) VALUES (?, ?)', (user_id, exercise_id))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Already favorite'}), 400

    if request.method == 'DELETE':
        data = request.json
        exercise_id = data.get('exercise_id')
        conn.execute('DELETE FROM favorites WHERE user_id = ? AND exercise_id = ?', (user_id, exercise_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})


if __name__ == '__main__':
    init_db()
    print("Veritabani basariyla olusturuldu!")
    print("Server baslatiliyor...")
    print("Tarayicinizda http://localhost:5000 adresini acin")
    app.run(debug=True, port=5000)
