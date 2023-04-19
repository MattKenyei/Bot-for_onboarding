import sqlite3

# создаем подключение к базе данных
conn = sqlite3.connect('workers.db')

# создаем курсор для выполнения запросов
cursor = conn.cursor()

# получаем всех работников из таблицы
cursor.execute('SELECT * FROM workers')
rows = cursor.fetchall()

# выводим результаты на экран
for row in rows:
    print(row)

# закрываем подключение
conn.close()
