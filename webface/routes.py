from . import app
from flask import render_template, request, redirect, url_for, session, flash
import functools
from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3

dbfile= 'databaze.sqlite'


slova = ("Super", "Perfekt", "Úža", "Flask")


def prihlasit(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if "user" in session:
            return function(*args, **kwargs)
        else:
            return redirect(url_for("login", url=request.path))

    return wrapper


@app.route("/", methods=["GET"])
def index():
    if "nick" in session:
        with sqlite3.connect(dbfile) as conn:
            tabulka = conn.execute('SELECT nick, text, id FROM prispevek')
        return render_template("base.html.j2", tabulka=tabulka)
    else:
        flash("Pro vstup na nástěnku je potřeba je přihlásit","error")
        return redirect(url_for("login"))



@app.route("/login/")
def login():
    return render_template("login.html.j2")


@app.route("/login/", methods=['POST'])
def login_post():
    nick=request.form.get("nick")
    passwd=request.form.get("passwd")
    if nick and passwd:
        with sqlite3.connect(dbfile) as conn:
            tabulka = list(conn.execute("SELECT passwd FROM uzivatel WHERE nick=?", [nick]))
        if tabulka and check_password_hash(tabulka[0][0], passwd):
            flash("Úspěšné přihlášení", "success")
            session["nick"] = nick
        else:
            flash("Špatné údaje", "error")
    return redirect(url_for("index"))

@app.route("/logout/")
def logout():
    session.pop("nick", None)
    return redirect(url_for("index"))


@app.route("/add/")
def add():
    return render_template("add.html.j2")
    nick=request.form.get('nick')
    passwd=request.fomr.get('passwd')


@app.route("/add/", methods=['POST'])
def add_post():
    nick=request.form.get('nick')
    passwd1=request.form.get('passwd1')
    passwd2=request.form.get('passwd2')
    if nick and passwd1 and passwd2 == passwd1:
        hashpasswd = generate_password_hash(passwd1)
        with sqlite3.connect(dbfile) as conn:
            try:
                conn.execute('INSERT INTO uzivatel (nick, passwd) VALUES (?,?)', [nick, hashpasswd])
                flash("Uživatel vytvořen.", "success")
                session["nick"] = nick
            except sqlite3.IntegrityError:
                flash("Uživatel již existuje", "error")
    else:
        flash("Chyba: je nutné zadat jméno a dvakrát stejné heslo", "error")
        return redirect(url_for("add"))
    return redirect(url_for("index"))

@app.route('/insert/', methods=["POST"])
def insert():
    if 'nick' in session:
        prispevek = request.form.get('prispevek')
        with sqlite3.connect(dbfile) as conn:
            conn.execute('INSERT INTO prispevek (text, nick) VALUES (?,?)', [prispevek, session['nick']])
        return redirect(url_for('index'))
    else:
        return abort(403)

@app.route('/delete/', methods=["POST"])
def delete():
    if 'nick' in session:
        idprisp=request.form.get('id')
        name=session["nick"]
        with sqlite3.connect(dbfile) as conn:
            conn.execute('DELETE FROM prispevek WHERE id=(?) AND nick=(?)', [idprisp, name])
        return redirect(url_for('index'))
    else:
        return abort(403)

@app.route('/editpost/', methods=["POST"])
def editpost():
    if 'nick' in session:
        session.pop("zaznam", None)
        idprisp=request.form.get('id')
        name=session["nick"]
        with sqlite3.connect(dbfile) as conn:
            zaznam = list(conn.execute('SELECT id, text, nick FROM prispevek WHERE id=(?) AND nick=(?)', [idprisp, name]))
        session["zaznam"]=zaznam
        return redirect(url_for('edit'))
    else:
        return abort(403)

@app.route('/edit/')
def edit():
    zaznam=session["zaznam"]
    text=zaznam[0][1]
    print(zaznam)
    return render_template("edit.html.j2", text=text)

@app.route('/editovat/', methods=["POST"])
def editovat():
    zaznam=session["zaznam"]
    name=session["nick"]
    upraveny=request.form.get('uprava')
    id=zaznam[0][0]
    with sqlite3.connect(dbfile) as conn:
        conn.execute('UPDATE prispevek SET text=(?) WHERE id=(?) AND nick=(?)', [upraveny, id, name])
    return redirect(url_for('index'))