import collections
from flask import Flask, render_template, request, redirect, session, json
from flask_session import Session
from flask_mysqldb import MySQL
import yaml

db = yaml.load(open("db.yaml"))


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_PORT"] = db["mysql_port"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]
mysql = MySQL(app)

@app.route("/")
def contact():
    if "loggedin" in session:
        return render_template("contact.html", username=session["username"])
    return redirect("/login")

@app.route("/login", methods = ["GET", "POST"])
def login():
    msg=''
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        cur = mysql.connection.cursor()
        cur.execute("select * from users where username=%s and password=%s", (name, password,))

        account = cur.fetchone()
        cur.close()

        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return redirect("/")
        else:
            msg = "incorrect username or password"
    
    return render_template("login.html", msg=msg)

@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect("/")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        cur = mysql.connection.cursor()
        cur.execute("insert into users (username, password, email) values (%s, %s, %s)", (username, password, email,))
        mysql.connection.commit()
        cur.execute("select * from users where username=%s and password=%s", (username, password,))

        account = cur.fetchone()
        cur.close()

        session['loggedin'] = True
        session['id'] = account[0]
        session['username'] = account[1]
        return redirect("/")

    else:
        cur = mysql.connection.cursor()
        cur.execute("select username, email from users")

        account = cur.fetchall()
        cur.close()
        
        results = []
        for acc in account:
            d = collections.OrderedDict()
            d['username'] = acc[0]
            d['email'] = acc[1]
            results.append(d)

        return render_template("register.html", result = json.dumps(results, sort_keys=False))