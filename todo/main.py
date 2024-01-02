from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import yaml
from tkinter import *
import sys

from yaml import load


app = Flask(__name__)

# Configure db
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']


app.secret_key = "super secret key"
mysql = MySQL(app)



@app.route('/', methods =['GET', 'POST'])
def front():
    msg = ''
    if request.method == 'POST':

        userDetails = request.form
        password = userDetails['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM login WHERE password = %s', (password,))
        account = cur.fetchone()
        if account:

            session['logged'] = True
            session['email'] = account[0]

            return redirect(url_for("home"))
        else:
            msg = 'Incorrect username / password !'
        cur.close()
    return render_template('front.html', msg=msg)


@app.route('/home')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `todo2`")
    todo_list = cur.fetchall()

    return render_template('base.html', todo_list=todo_list)


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method=='POST':
        userDetails = request.form
        name = userDetails['name']
        date = userDetails['date']
        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO `todo2` (`name`,`date`,`done`) VALUES ('{name}','{date}','0')")
        mysql.connection.commit()
        return redirect(url_for('home'))
    else:
        return render_template('base.html')

@app.route('/delete/<int:task_id>', methods = ['GET'])
def delete(task_id):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM todo2 WHERE task_id=%s", (task_id,))
    mysql.connection.commit()
    return redirect(url_for('home'))


@app.route('/update/<int:task_id>')
def update(task_id):
    cur = mysql.connection.cursor()
    # cur.execute("SELECT done FROM todo2 WHERE task_id=%s", (task_id,))
    cur.execute("""   UPDATE todo2 SET done=not done WHERE task_id=%s""", (task_id,))
    mysql.connection.commit()
    return redirect(url_for("home"))


@app.route('/logout')
def logout():
    session.pop('logged', None)
    session.pop('email', None)
    return redirect(url_for('front'))

if __name__ == '__main__':
    app.run(debug=True, port=8001)