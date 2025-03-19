from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sqlite3 as sql
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey'

con = sql.connect('database.db')
print ("Oppened database successfully")

con.execute("PRAGMA foreign_keys = ON")

con.execute('CREATE TABLE IF NOT EXISTS users (id_user INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, username TEXT, password TEXT, id_kartu TEXT, role TEXT CHECK(role IN ("admin", "user")))')
print("Table users created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS lab (id_lab INTEGER PRIMARY KEY AUTOINCREMENT, nama_lab TEXT, url_micro TEXT NULL)')
print("Table lab created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS inventaris (id_barang INTEGER PRIMARY KEY AUTOINCREMENT, nama_barang TEXT, jumlah_barang INTEGER, kondisi TEXT CHECK(kondisi IN ("baik", "rusak")), deskripsi TEXT, id_lab INTEGER, FOREIGN KEY (id_lab) REFERENCES lab(id_lab))')
print("Table inventaris created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS penjadwalan (id_penjadwalan INTEGER PRIMARY KEY AUTOINCREMENT, id_lab INTEGER, id_user INTEGER, start_time DATETIME, end_time DATETIME, status TEXT CHECK(status IN ("pending", "approve", "reject")), FOREIGN KEY (id_lab) REFERENCES lab(id_lab), FOREIGN KEY (id_user) REFERENCES users(id_user))')
print("Table penjadwalan created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS log (id_log INTEGER PRIMARY KEY AUTOINCREMENT, id_kartu TEXT, id_lab INTEGER, timestamp DATETIME )')
print("Table log created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS peminjaman (id_peminjaman INTEGER PRIMARY KEY AUTOINCREMENT, id_user INTEGER, tanggal_pinjam DATETIME, tanggal_kembali DATETIME, status TEXT CHECK(status IN ("pending", "approve", "reject", "returned", "late")), FOREIGN KEY (id_user) REFERENCES users(id_user))')
print("Table peminjaman created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS detail_peminjaman (id_detail INTEGER PRIMARY KEY AUTOINCREMENT, id_peminjaman INTEGER, id_barang INTEGER, kondisi TEXT CHECK(kondisi IN ("baik", "rusak")), deskripsi TEXT, FOREIGN KEY (id_barang) REFERENCES barang(id_barang), FOREIGN KEY (id_peminjaman) REFERENCES peminjaman(id_peminjaman))')
print("Table detail_peminjaman created succesfully")
con.close()

def get_db_connection():
    conn = sql.connect('database.db')
    conn.row_factory = sql.Row  # Agar hasil query bisa diakses seperti dictionary
    return conn

def md5(text):
    return hashlib.md5(text.encode()).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = md5(request.form['password'])

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        print(user)

        if user:
            session['id_user'] = user['id_user']
            session['username'] = user['username']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'static']
    if 'id_user' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

# START ADMIN

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# READ - Menampilkan data User
@app.route('/admin/user')
def admin_user():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin_user.html', users=users)

# CREATE atau UPDATE User (Gabung Tambah & Edit)
@app.route('/admin/user/save', methods=['POST'])
def save_user():
    id_user = request.form.get('id_user')
    nama = request.form['nama']
    username = request.form['username']
    password = md5(request.form['password'])
    id_kartu = request.form['id_kartu']
    role = request.form['role']
    
    conn = get_db_connection()
    
    if id_user:  # Jika ada ID, berarti Edit
        conn.execute('UPDATE users SET nama = ?, username = ?, password = ?, id_kartu = ?, role = ? WHERE id_user = ?', (nama, username, password, id_kartu, role, id_user))
    else:  # Jika tidak ada ID, berarti Tambah
        conn.execute('INSERT INTO users (nama, username, password, id_kartu, role) VALUES (?, ?, ?, ?, ?)', (nama, username, password, id_kartu, role))
    
    conn.commit()
    conn.close()
    return redirect(url_for('admin_user'))

# DELETE - Menghapus data User
@app.route('/admin/user/delete/<int:id>', methods=['POST'])
def delete_user(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id_user = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_user'))

# READ - Menampilkan data Ruang
@app.route('/admin/ruang')
def admin_ruang():
    conn = get_db_connection()
    ruang = conn.execute('SELECT * FROM lab').fetchall()
    conn.close()
    return render_template('admin_ruang.html', ruang=ruang)

# CREATE atau UPDATE Ruang (Gabung Tambah & Edit)
@app.route('/admin/ruang/save', methods=['POST'])
def save_ruang():
    id_lab = request.form.get('id_lab')
    nama_lab = request.form['nama_lab']
    url_micro = request.form['url_micro']
    
    conn = get_db_connection()
    
    if id_lab:  # Jika ada ID, berarti Edit
        conn.execute('UPDATE lab SET nama_lab = ?, url_micro = ? WHERE id_lab = ?', (nama_lab, url_micro, id_lab))
    else:  # Jika tidak ada ID, berarti Tambah
        conn.execute('INSERT INTO lab (nama_lab, url_micro) VALUES (?, ?)', (nama_lab, url_micro))
    
    conn.commit()
    conn.close()
    return redirect(url_for('admin_ruang'))

# DELETE - Menghapus data Ruang
@app.route('/admin/ruang/delete/<int:id>', methods=['POST'])
def delete_ruang(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM lab WHERE id_lab = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_ruang'))

# READ - Menampilkan data Barang
@app.route('/admin/barang')
def admin_barang():
    conn = get_db_connection()
    barang = conn.execute('SELECT * FROM inventaris join lab on inventaris.id_lab = lab.id_lab').fetchall()
    ruang = conn.execute('SELECT * FROM lab').fetchall()
    conn.close()
    return render_template('admin_barang.html', barang=barang, ruang=ruang)

# CREATE atau UPDATE Barang (Gabung Tambah & Edit)
@app.route('/admin/barang/save', methods=['POST'])
def save_barang():
    id_barang = request.form.get('id_barang')
    nama_barang = request.form['nama_barang']
    jumlah_barang = request.form['jumlah_barang']
    kondisi = request.form['kondisi']
    deskripsi = request.form['deskripsi']
    id_lab = request.form['id_lab']
    
    conn = get_db_connection()
    
    if id_barang:  # Jika ada ID, berarti Edit
        conn.execute('UPDATE inventaris SET nama_barang = ?, jumlah_barang = ?, kondisi = ?, deskripsi = ?, id_lab = ? WHERE id_barang = ?', (nama_barang, jumlah_barang, kondisi, deskripsi, id_lab, id_barang))
    else:  # Jika tidak ada ID, berarti Tambah
        conn.execute('INSERT INTO inventaris (nama_barang, jumlah_barang, kondisi, deskripsi, id_lab) VALUES (?, ?, ?, ?, ?)', (nama_barang, jumlah_barang, kondisi, deskripsi, id_lab))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_barang'))

# DELETE - Menghapus data Barang
@app.route('/admin/barang/delete/<int:id>', methods=['POST'])
def delete_barang(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM inventaris WHERE id_barang = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_barang'))

@app.route('/admin/pinjam')
def admin_pinjam():
    conn = get_db_connection()
    peminjaman = conn.execute("""
        SELECT p.id_peminjaman, u.nama AS username, p.tanggal_pinjam, p.tanggal_kembali, p.status,
            GROUP_CONCAT(b.nama_barang, ', ') AS barang_dipinjam
        FROM peminjaman p
        JOIN users u ON p.id_user = u.id_user
        LEFT JOIN detail_peminjaman dp ON p.id_peminjaman = dp.id_peminjaman
        LEFT JOIN inventaris b ON dp.id_barang = b.id_barang
        GROUP BY p.id_peminjaman
    """).fetchall()
    users = conn.execute("SELECT * FROM users").fetchall()
    barang_list = conn.execute("SELECT * FROM inventaris").fetchall()
    conn.close()

    # Konversi string ke datetime
    formatted_peminjaman = []
    for p in peminjaman:
        formatted_peminjaman.append({
            "id_peminjaman": p["id_peminjaman"],
            "username": p["username"],
            "tanggal_pinjam": datetime.strptime(p["tanggal_pinjam"], "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S"),
            "tanggal_kembali": datetime.strptime(p["tanggal_kembali"], "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S"),
            "barang_dipinjam": p["barang_dipinjam"],
            "status": p["status"]
        })
    return render_template('admin_pinjam.html', peminjaman=formatted_peminjaman, users=users, barang_list=barang_list)

@app.route('/admin/pinjam/tambah', methods=['POST'])
def add_peminjaman():
    id_user = request.form['id_user']
    tanggal_pinjam = request.form['tanggal_pinjam']
    tanggal_kembali = request.form['tanggal_kembali']
    id_barang_list = request.form.getlist('id_barang[]')
    status = "approve"

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO peminjaman (id_user, tanggal_pinjam, tanggal_kembali, status) VALUES (?, ?, ?, ?)", 
                   (id_user, tanggal_pinjam, tanggal_kembali, status))
    id_peminjaman = cursor.lastrowid

    for id_barang in id_barang_list:
        cursor.execute("INSERT INTO detail_peminjaman (id_peminjaman, id_barang, kondisi, deskripsi) VALUES (?, ?, ?, ?)", 
                       (id_peminjaman, id_barang, "baik", "Dipinjam"))

    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_pinjam'))

@app.route('/admin/pinjam/approve/<int:id>', methods=['POST'])
def approve_peminjaman(id):
    conn = get_db_connection()
    conn.execute("UPDATE peminjaman SET status = 'approve' WHERE id_peminjaman = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Peminjaman disetujui'})

@app.route('/admin/pinjam/reject/<int:id>', methods=['POST'])
def reject_peminjaman(id):
    conn = get_db_connection()
    conn.execute("UPDATE peminjaman SET status = 'reject' WHERE id_peminjaman = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Peminjaman ditolak'})

@app.route('/admin/pinjam/returned/<int:id>', methods=['POST'])
def kembalikan_barang(id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Ambil tanggal kembali dari database
    cur.execute("SELECT tanggal_kembali FROM peminjaman WHERE id_peminjaman = ?", (id,))
    row = cur.fetchone()
    
    if not row or not row[0]:  
        return jsonify({'success': False, 'message': 'Data peminjaman tidak ditemukan'}), 404

    # Konversi format dengan "T"
    tanggal_kembali_db = datetime.fromisoformat(row[0])  # Format otomatis mendukung "T"
    sekarang = datetime.now()

    # Cek keterlambatan
    status_baru = 'late' if sekarang > tanggal_kembali_db else 'returned'

    # Update status dan tanggal kembali
    cur.execute("""
        UPDATE peminjaman 
        SET status = ?, tanggal_kembali = ? 
        WHERE id_peminjaman = ?
    """, (status_baru, sekarang.isoformat(timespec='minutes'), id))  # Simpan format dengan "T"

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'Barang berhasil dikembalikan dengan status {status_baru}'})

@app.route('/admin/jadwal')
def admin_jadwal():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    ruangs = conn.execute("SELECT * FROM lab").fetchall()
    jadwal = conn.execute("SELECT * FROM penjadwalan JOIN lab ON penjadwalan.id_lab = lab.id_lab JOIN users ON penjadwalan.id_user = users.id_user").fetchall()
    conn.close()
    # Konversi string ke datetime
    formatted_jadwal = []
    for p in jadwal:
        formatted_jadwal.append({
            "id_penjadwalan": p["id_penjadwalan"],
            "nama": p["nama"],
            "nama_lab": p["nama_lab"],
            "start_time": datetime.strptime(p["start_time"], "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.strptime(p["end_time"], "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S"),
            "status": p["status"]
        })
    return render_template('admin_jadwal.html', users = users, ruangs = ruangs, jadwal = formatted_jadwal)

@app.route('/admin/jadwal/tambah', methods=['POST'])
def add_penjadwalan():
    id_user = request.form['id_user']
    id_lab = request.form['id_lab']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    status = "pending"

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO penjadwalan (id_user, id_lab, start_time, end_time, status) VALUES (?, ?, ?, ?, ?)", 
                   (id_user, id_lab, start_time, end_time, status))

    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_jadwal'))

@app.route('/admin/jadwal/approve/<int:id>', methods=['POST'])
def approve_penjadwalan(id):
    conn = get_db_connection()
    conn.execute("UPDATE penjadwalan SET status = 'approve' WHERE id_penjadwalan = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Penjadwalan disetujui'})

@app.route('/admin/jadwal/reject/<int:id>', methods=['POST'])
def reject_jadwal(id):
    conn = get_db_connection()
    conn.execute("UPDATE penjadwalan SET status = 'reject' WHERE id_penjadwalan = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Penjadwalan ditolak'})

@app.route('/admin/log')
def admin_log():
    conn = get_db_connection()
    log = conn.execute('SELECT * FROM log JOIN lab ON log.id_lab = lab.id_lab JOIN users ON log.id_kartu = users.id_kartu').fetchall()
    # log = conn.execute('SELECT * FROM log').fetchall()
    conn.close()
    return render_template('admin_log.html', log=log)

# END ADMIN

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__=='__main__':
    app.run(debug=True, port=5000)