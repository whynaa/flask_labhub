from flask import Flask, render_template, request
import sqlite3 as sql

app = Flask(__name__)
con = sql.connect('database.db')
print ("Oppened database successfully")

con.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT, address TEXT, city TEXT, pin TEXT)')
print("Table created succesfully")
con.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/form_student")
def form_student():
    return render_template('student.html')

@app.route("/add_student", methods=['POST', 'GET'])
def add_student():
    message = "message"
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            address = request.form['address']
            city = request.form['city']
            pin = request.form['pin']
            with sql.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO students (name, email, password, address, city, pin) VAlUES(?,?,?,?,?,?)", (name, email, password, address, city, pin))
                con.commit()
                message = "Student Added Successfully"
        except:
            con.rollback()
            message = "Error in inserting student data"
        finally:
            return render_template("result.html", message=message)

@app.route('/list_student')
def list_student():
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM students")
    rows = cur.fetchall()
    return render_template("list_student.html", rows=rows)

if __name__=='__main__':
    app.run(debug=True, port=5010)