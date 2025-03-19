from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql

app = Flask(__name__)
con = sql.connect('database.db')
print ("Oppened database successfully")

con.execute("PRAGMA foreign_keys = ON")

con.execute('CREATE TABLE IF NOT EXISTS users (id_user INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, username TEXT, password TEXT, id_kartu TEXT, role TEXT CHECK(role IN ("admin", "user")))')
print("Table users created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS lab (id_lab INTEGER PRIMARY KEY AUTOINCREMENT, nama_lab TEXT)')
print("Table lab created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS inventaris (id_barang INTEGER PRIMARY KEY AUTOINCREMENT, nama_barang TEXT, jumlah_barang INTEGER, kondisi TEXT CHECK(kondisi IN ("baik", "rusak")), deskripsi TEXT, id_lab INTEGER, FOREIGN KEY (id_lab) REFERENCES lab(id_lab))')
print("Table inventaris created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS penjadwalan (id_penjadwalan INTEGER PRIMARY KEY AUTOINCREMENT, id_lab INTEGER, id_user INTEGER, start_time DATETIME, end_time DATETIME, status TEXT CHECK(status IN ("pending", "approve", "reject")), FOREIGN KEY (id_lab) REFERENCES lab(id_lab), FOREIGN KEY (id_user) REFERENCES users(id_user))')
print("Table penjadwalan created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS log (id_log INTEGER PRIMARY KEY AUTOINCREMENT, id_kartu INTEGER, timestamp DATETIME, FOREIGN KEY (id_kartu) REFERENCES user(id_kartu) )')
print("Table log created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS peminjaman (id_peminjaman INTEGER PRIMARY KEY AUTOINCREMENT, id_user INTEGER, tanggal_pinjam DATETIME, tanggal_kembali DATETIME, status TEXT CHECK(status IN ("pending", "approve", "returned", "late")), FOREIGN KEY (id_user) REFERENCES users(id_user))')
print("Table peminjaman created succesfully")

con.execute('CREATE TABLE IF NOT EXISTS detail_peminjaman (id_detail INTEGER PRIMARY KEY AUTOINCREMENT, id_peminjaman INTEGER, id_barang INTEGER, kondisi TEXT CHECK(kondisi IN ("baik", "rusak")), deskripsi TEXT, FOREIGN KEY (id_barang) REFERENCES barang(id_barang), FOREIGN KEY (id_peminjaman) REFERENCES peminjaman(id_peminjaman))')
print("Table detail_peminjaman created succesfully")
con.close()

def get_db_connection():
    conn = sql.connect('database.db')
    conn.row_factory = sql.Row  # Agar hasil query bisa diakses seperti dictionary
    return conn


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

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
    password = request.form['password']
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
    
    conn = get_db_connection()
    
    if id_lab:  # Jika ada ID, berarti Edit
        conn.execute('UPDATE lab SET nama_lab = ? WHERE id_lab = ?', (nama_lab, id_lab))
    else:  # Jika tidak ada ID, berarti Tambah
        conn.execute('INSERT INTO lab (nama_lab) VALUES (?)', (nama_lab,))
    
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
    print(barang)
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
    return render_template('admin_pinjam.html')

@app.route('/admin/jadwal')
def admin_jadwal():
    return render_template('admin_jadwal.html')

@app.route('/admin/log')
def admin_log():
    return render_template('admin_log.html')

# END ADMIN

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__=='__main__':
    app.run(debug=True, port=5000)