#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

from flask import Flask, flash, render_template, request, g, session, redirect, url_for
import mysql.connector, hashlib, urllib, datetime, time, os, telegram
from mysql.connector import Error
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from slackclient import SlackClient


app = Flask(__name__)


app.config.from_object('secret_config')

def connect_db () :
    g.mysql_connection = mysql.connector.connect(
        host = app.config['DATABASE_HOST'],
        user = app.config['DATABASE_USER'],
        password = app.config['DATABASE_PASSWORD'],
        database = app.config['DATABASE_NAME']
    )
    g.mysql_cursor = g.mysql_connection.cursor()
    return g.mysql_cursor

def get_db () :
    if not hasattr(g, 'db') :
        g.db = connect_db()
    return g.db

def newConnectDb() :
    mysql_connection = mysql.connector.connect(
        host = app.config['DATABASE_HOST'],
        user = app.config['DATABASE_USER'],
        password = app.config['DATABASE_PASSWORD'],
        database = app.config['DATABASE_NAME']
    )
    return mysql_connection

def getHttpCode (url) :
    try :
        request = urllib.request.urlopen(url)
        return request.getcode()
    except urllib.error.HTTPError as error :
        return error.code
    except urllib.error.URLError as error :
        return error.reason

def isUrlCorrect (url) :
    try :
        request = urllib.request.urlopen(url)
        return True
    except urllib.error.URLError as error :
        return error.reason

def getStatus(sites) :
    status = []
    for site in sites :
        status.append(getHttpCode(site[1]))
    return status

def insertStatusCode () :
    db = get_db()
    db.execute("SELECT id, url FROM sites")
    sites = db.fetchall()
    date = datetime.datetime.now()
    datas = []

    for site in sites:
        code = getHttpCode(site[1])
        datas.append((site[0], code, date))

    sql = "INSERT INTO status VALUES(DEFAULT, %s, %s, %s)"
    db.executemany(sql, datas)
    g.mysql_connection.commit()

def autoInsertStatusCode () :
    db = newConnectDb()
    cursor = db.cursor()
    cursor.execute("SELECT id, url FROM sites")
    sites = cursor.fetchall()
    date = datetime.datetime.now()
    datas = []

    for site in sites:
        code = getHttpCode(site[1])
        if code != 200 :
            if isDown(site[0]) :
                sendSlackMessage(site[1], code)
                sendTelegramMessage(site[1], code)
        datas.append((site[0], code, date))

    sql = "INSERT INTO status VALUES(DEFAULT, %s, %s, %s)"
    cursor.executemany(sql, datas)
    db.commit()
    cursor.close()
    db.close()

def sendSlackMessage (url, code) :
    slack_token = app.config['SLACK_TOKEN']
    sc = SlackClient(slack_token)
    sc.api_call(
        "chat.postMessage",
        channel=app.config['SLACK_CHANNEL'],
        text="Bonjour, il semblerait qu'il y ai un problème avec votre site "+ url +". Statut : "+ str(code)
    )

def sendTelegramMessage (url, code) :
    telegram_token = app.config['TELEGRAM_TOKEN']
    bot = telegram.Bot(token=telegram_token)
    bot.send_message(chat_id=app.config['TELEGRAM_CHAT_ID'], text="Bonjour, il semblerait qu'il y ai un problème avec votre site "+ url +". Statut : "+ str(code))

def isDown (id) :
    db = newConnectDb()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM status WHERE site_id = %(id)s ORDER BY date DESC LIMIT 3", {'id' : id})
    lastStatus = cursor.fetchall()
    for status in lastStatus :
        if status[2] != 200 :
            return False
    return True


# Ferme les BDD à la fin de l'execution
@app.teardown_appcontext
def close_db (error) :
    if hasattr(g, 'db') :
        g.db.close()


# Routes

@app.route('/')
def index () :
    if session.get('user') :
        user = session['user']
    else :
        user = False

    db = get_db()
    db.execute("SELECT id, url FROM sites")
    sites = db.fetchall()
    status = getStatus(sites)

    return render_template('home.html.j2', user = user, sites = sites, status = status)

@app.route('/login/', methods = ['GET', 'POST'])
def login () :
    name = str(request.form.get('name'))
    password = str(request.form.get('password'))

    db = get_db()
    db.execute('SELECT name, password FROM user WHERE name = %(name)s', {'name' : name})
    users = db.fetchall()

    valid_user = False
    for user in users :
        if hashlib.sha256(password.encode('ascii')).hexdigest() == user[1]:
            valid_user = user

    if valid_user :
        session['user'] = valid_user
        return redirect(url_for('admin'))

    return render_template('login.html.j2')

@app.route('/logout/')
def logout () :
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/')
def admin () :
    if not session.get('user') or not session.get('user')[1] :
        return redirect(url_for('login'))

    db = get_db()
    db.execute("SELECT id, url FROM sites")
    sites = db.fetchall()
    status = getStatus(sites)
    # insertStatusCode()
    # sendSlackMessage()
    # sendTelegramMessage()

    return render_template('admin.html.j2', user = session['user'], sites = sites, status = status)

@app.route('/admin/add/', methods = ['GET', 'POST'])
def add () :
    if not session.get('user') or not session.get('user')[1] :
        return redirect(url_for('login'))

    url = request.form.get('url')

    if url is not None:
        db = get_db()
        if type(getHttpCode(url)) is int :
            db.execute("INSERT INTO sites(id, url) VALUES(DEFAULT, '%s')"%(str(url)))
            g.mysql_connection.commit()
            flash("Le site " + url + " a bien été ajouté à la liste")
            return redirect(url_for('admin'))
        else :
            flash("Le site " + url + " ne semble pas exister ou n'autorise pas que vous l'analysiez")
    return render_template('add.html.j2', user = session['user'])

@app.route('/admin/edit/<int:id>', methods = ['GET', 'POST'])
def edit (id) :
    if not session.get('user') or not session.get('user')[1] :
        return redirect(url_for('login'))

    db = get_db()
    url = request.form.get('url')

    db.execute("SELECT url FROM sites WHERE id = %s"%(id))
    site = db.fetchone()

    if url is None:
        if site is not None :
            return render_template('edit.html.j2', site = site[0], user = session['user'])
        else :
            flash("Ce site ne semble pas exister")
            return redirect(url_for('admin'))
    else:
        if (isUrlCorrect(url) == True) :
            db.execute("UPDATE sites SET url = '%s' WHERE id = %s"%(str(url), id))
            g.mysql_connection.commit()
            flash("Le site ayant l'id " + str(id) + " a bien été modifié avec la valeur " + url)
            return redirect(url_for('admin'))
        else :
            flash("Le site " + url + " ne semble pas exister ou n'autorise pas que vous l'analysiez")
            return render_template('edit.html.j2', site = site[0], user = session['user'])

@app.route('/admin/delete/<int:id>')
def delete (id) :
    if not session.get('user') or not session.get('user')[1] :
        return redirect(url_for('login'))

    db = get_db()
    db.execute("DELETE FROM sites WHERE id = %s"%(id))
    g.mysql_connection.commit()

    if db.rowcount > 0 :
        flash("Le site ayant l'id " + str(id) + " a bien été supprimé")
    else :
        flash("Le site ayant l'id " + str(id) + " n'a pas pu être supprimé")

    return redirect(url_for('admin'))

@app.route('/history/<int:id>')
def history (id) :
    if session.get('user') :
        user = session['user']
    else :
        user = False

    db = get_db()
    db.execute("SELECT st.*, si.url FROM status st INNER JOIN sites si ON si.id = st.site_id WHERE site_id = %s ORDER BY date DESC"%(id))
    status = db.fetchall()
    return render_template('history.html.j2', user = user, status = status)

with app.app_context():
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=autoInsertStatusCode,
            trigger=IntervalTrigger(seconds=10),
            replace_existing=True,
        )
        scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
