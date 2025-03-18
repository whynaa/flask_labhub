from flask import Flask, render_template, request
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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__=='__main__':
    app.run(debug=True, port=5000)