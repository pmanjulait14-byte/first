from flask import Flask, render_template
from flask import request
from flask import redirect
from flask import session
import sqlite3

app = Flask(__name__)

app.secret_key = "my_secret_key"

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/submit', methods=['POST'])
def submit():

    name = request.form.get("name")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name) VALUES (?)",
        (name,)
    )

    conn.commit()
    conn.close()

    return f"{name} saved successfully"

@app.route('/students')
def students():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students
    )

@app.route('/update/<int:id>', methods=['POST'])
def update(id):

    name = request.form.get('name')

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE students SET name=? WHERE id=?",
        (name, id)
    )

    conn.commit()
    conn.close()

    return redirect('/students')

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user=session["user"]
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE username=?
            AND password=?
            """,
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)