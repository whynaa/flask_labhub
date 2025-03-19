from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = "your_secret_key"
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

@app.route('/admin/user')
def admin_user():
    return render_template('admin_user.html')

@app.route('/admin/ruang')
def admin_ruang():
    return render_template('admin_ruang.html')

@app.route('/admin/barang')
def admin_barang():
    return render_template('admin_barang.html')

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

# START USER
@app.route('/user/dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/user/profile', methods=["POST","GET"])
def user_profile():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users where id_user=1').fetchone()
    conn.close()
    return render_template('user_profile.html', users=users)

@app.route('/user/profile/save', methods=['POST'])
def update_user():
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
    return redirect(url_for('user_profile'))


#Menampikan data ruang
@app.route('/user/ruang')
def user_ruang():
    conn = get_db_connection()
    labs = conn.execute('SELECT * FROM lab').fetchall()
    conn.close()
    return render_template('user_ruang.html', labs=labs)

#Pinjam Lab
@app.route('/user/user_jadwal', methods=['GET', 'POST'])
def peminjaman():
    conn = get_db_connection()
    lab_list = conn.execute('SELECT * FROM lab').fetchall()
    user_list = conn.execute('SELECT * FROM users').fetchall()
    
    if request.method == 'POST':
        id_user = request.form['nama']
        jam_mulai = request.form['jam_mulai']
        jam_selesai = request.form['jam_selesai']
        id_lab = request.form.get('id_lab') 

        try:
            conn.execute(
                "INSERT INTO penjadwalan (id_lab, id_user, start_time, end_time, status) VALUES (?, ?, ?, ?, ?)",
                (id_lab, id_user, jam_mulai, jam_selesai, "pending") 
            )
            conn.commit()
            flash("✅ Peminjaman berhasil diajukan!", "success")
            return redirect(url_for('user_ruang')) 
        except Exception as e:
            flash(f"⚠️ Terjadi kesalahan: {e}", "danger")
        
        conn.close()
        return redirect(url_for('peminjaman'))

    conn.close()
    return render_template('user_jadwal.html', lab_list=lab_list, user = user_list)

#Riwayat Peminjaman Lab
@app.route('/user/log_lab')
def riwayat_lab():
    conn = get_db_connection()
    pinjam = conn.execute(' SELECT j.id_penjadwalan, u.id_kartu, l.nama_lab, j.start_time, j.end_time FROM penjadwalan j JOIN lab l ON j.id_lab = l.id_lab JOIN users u ON j.id_user = u.id_user WHERE j.id_user=1').fetchall() 
    conn.close()
    return render_template('user_log_lab.html', peminjaman = pinjam)

@app.route('/user/barang')
def user_barang():
    conn = get_db_connection()
    barang = conn.execute('SELECT * FROM inventaris join lab on inventaris.id_lab = lab.id_lab').fetchall()
    ruang = conn.execute('SELECT * FROM lab').fetchall()
    conn.close()
    print(barang)
    return render_template('user_barang.html', barang=barang, ruang=ruang)

@app.route('/user/jadwal')
def user_jadwal():
    return render_template('user_jadwal.html')

@app.route('/user/log')
def user_log():
    return render_template('user_log.html')



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__=='__main__':
    app.run(debug=True, port=5000)