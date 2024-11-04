from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector as cnx
from datetime import datetime, timedelta

import calendar

app = Flask(__name__)

# Configuración de la base de datos
config = {
    "host": "GuadalupeGT.mysql.pythonanywhere-services.com",
    "user": "GuadalupeGT",
    "password": "D@t4bAs3_paSs",
    "database": "GuadalupeGT$default",
    "ssl_disabled": True
}
app.secret_key = 'super_secret_key'
mysql = cnx.connect(**config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = username
            session['role'] = user[3]

            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', message="Las credenciales no son correctas")

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'user':
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' in session and session['role']  == 'admin':
        return render_template('admin_dashboard.html')
    return redirect(url_for('login'))

@app.route('/user/dashboard')
def user_dashboard():
    if 'username' in session and session['role'] == 'user':
        user_id = obtener_id_de_usuario(session['username'])
        consumption_data = obtener_consumo_de_energia(user_id)
        return render_template('user_dashboard.html', consumption_data=consumption_data)

    return redirect(url_for('login'))

def obtener_id_de_usuario(username):
    cur = mysql.cursor()
    cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    if user:
        return user[0]
    return None

def obtener_consumo_de_energia(user_id):
    cur = mysql.cursor()

    daily_consumption = []
    weekly_consumption = []
    monthly_consumption = []
    annual_consumption = []

    # Obtener consumo diario para los ultimos 7 dias
    for i in range(6, -1, -1):
        start_date = datetime.today().date() - timedelta(days=i)
        end_date = start_date
        cur.execute("SELECT SUM(energy_consumed) AS total FROM energy_consumption WHERE user_id = %s AND date BETWEEN %s AND %s",(user_id, start_date, end_date))
        daily_consumption.append(cur.fetchone()[0] or 0)

    # Obtener consumo semanal para las últimas 4 semanas
    for i in range(4, 0, -1):
        start_date = datetime.today().date() - timedelta(weeks=i)
        end_date = start_date + timedelta(days=6)
        cur.execute("SELECT SUM(energy_consumed) AS total FROM energy_consumption WHERE user_id = %s AND date BETWEEN %s AND %s",(user_id, start_date, end_date))
        weekly_consumption.append(cur.fetchone()[0] or 0)

    # Rango para los últimos 6 meses, incluyendo el mes actual
    for i in range(5, -1, -1):
        first_day_of_month = (datetime.today().replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        last_day_of_month = first_day_of_month.replace(day=calendar.monthrange(first_day_of_month.year, first_day_of_month.month)[1])

        cur.execute("SELECT SUM(energy_consumed) AS total FROM energy_consumption WHERE user_id = %s AND date BETWEEN %s AND %s",(user_id, first_day_of_month, last_day_of_month))
        monthly_consumption.append(cur.fetchone()[0] or 0)

    # Rango para los últimos 5 años
    current_year = datetime.today().year
    for i in range(4, -1, -1):
        year = current_year - i
        first_day_of_year = datetime(year, 1, 1)
        last_day_of_year = datetime(year, 12, 31)

        cur.execute("SELECT SUM(energy_consumed) AS total FROM energy_consumption WHERE user_id = %s AND date BETWEEN %s AND %s",(user_id, first_day_of_year, last_day_of_year))
        annual_consumption.append(cur.fetchone()[0] or 0)
    annual_consumption.reverse()

    cur.close()

    return {
        'daily': daily_consumption,
        'weekly': weekly_consumption,
        'monthly': monthly_consumption,
        'annual': annual_consumption
    }

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return render_template('index.html')
