import mysql.connector
from datetime import date, timedelta
import random

config = {
    "host": "GuadalupeGT.mysql.pythonanywhere-services.com",
    "user": "GuadalupeGT",
    "password": "D@t4bAs3_paSs",
    "database": "GuadalupeGT$default",
    "ssl_disabled": True
}

mysql = mysql.connector.connect(**config)
cursor = mysql.cursor()

user_ids = [8]
energy_range = (15.0, 80.0)
start_date_2021 = date(2021, 1, 1)
end_date_2022 = date(2024, 11, 1)
delta = timedelta(days=7)

current_date = start_date_2021
while current_date <= end_date_2022:
    for user_id in user_ids:
        energy_consumed = round(random.uniform(*energy_range), 2)
        cursor.execute("""
            INSERT INTO energy_consumption (user_id, date, energy_consumed)
            VALUES (%s, %s, %s)
        """, (user_id, current_date, energy_consumed))

    current_date += delta

mysql.commit()
print("Datos insertados correctamente para los años 2021 y 2022.")

cursor.close()
mysql.close()
