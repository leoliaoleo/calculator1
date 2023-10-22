import pymysql
import mysql.connector
from flask import Flask, request, jsonify,render_template, redirect
app = Flask(__name__)

# MySQL database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ' calculator'

# Connect to MySQL database
db = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    passwd=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)
cursor = db.cursor()

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'calculator',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

@app.route("/")
def calculator():
    return render_template("calculator.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    num1 = request.form['num1']
    num2 = request.form['num2']
    operation = request.form['operation']
    result = None

    # Perform calculation operation
    if operation == '+':
        result = float(num1) + float(num2)
    elif operation == '-':
        result = float(num1) - float(num2)
    elif operation == '*':
        result = float(num1) * float(num2)
    elif operation == '/':
        result = float(num1) / float(num2)

    calculation = f"{num1} {operation} {num2} = {result}"

    try:
        # Insert calculation expression into database
        cursor.execute("INSERT INTO history (calculation) VALUES (%s)", (calculation,))
        db.commit()
        return redirect("/")
    except mysql.connector.Error as e:
        print("Error occurred:", e)

    return "Error occurred while inserting data into database"


@app.route("/history", methods=['POST'])
def history():
    try:
        history = request.form['history']

        # 连接MySQL数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # 检查是否已经存在'calculation'列
        sql_check = "SELECT COUNT(*) as count FROM information_schema.columns WHERE table_name = 'history' AND column_name = 'calculation'"
        cursor.execute(sql_check)
        result_check = cursor.fetchone()
        if result_check['count'] == 0:
            # 执行 ALTER TABLE 语句以添加'calculation'列
            sql_alter = "ALTER TABLE history ADD calculation VARCHAR(255)"
            cursor.execute(sql_alter)
            conn.commit()

        # 将历史记录插入数据库中
        sql_insert = "INSERT INTO history (expression) VALUES (%s)"
        cursor.execute(sql_insert, (history,))
        conn.commit()

        # 关闭数据库连接
        cursor.close()
        conn.close()

        return "History saved successfully"
    except Exception as e:
        # 处理异常，例如打印错误信息等
        print(e)
        return "Error saving history"

@app.route("/history")
def view_history():
    try:
        # 连接MySQL数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # 从数据库中检索数据
        cursor.execute("SELECT calculation FROM history")
        result = cursor.fetchall()

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 提取检索到的结果并传递给模板进行渲染
        history = [row['calculation'] for row in result]
        return render_template("history.html", history=history)
    except Exception as e:
        # 处理异常，例如打印错误信息等
        print(e)
        return "Error occurred while retrieving data from database"

@app.route("/save", methods=["POST"])
def save_to_database():
    try:
        print("调用 save_to_database 函数之前")
        data = request.get_json()
        calculation = data["calculation"]
        print(calculation)
        sql = "INSERT INTO history (calculation) VALUES (%s)"
        values = (calculation, )
        cursor.execute(sql, values)
        db.commit()
        return jsonify({"message": "Data saved to database"})
    except mysql.connector.Error as e:
        return "Error occurred while saving data to database"



@app.route("/clear")
def clear():
    try:
        # Clear the history table
        cursor.execute("DELETE FROM history")
        db.commit()
        return redirect("/history")
    except mysql.connector.Error as e:
        return "Error occurred while clearing the database"

@app.route("/save_history.php", methods=["POST"])
def save_history_to_database():
    try:
        print("调用 save_history_to_database 函数之前")
        data = request.get_json()
        history = data["history"]
        print(history)
        sql = "INSERT INTO history (calculation) VALUES (%s)"
        values = (history, )
        cursor.execute(sql, values)
        db.commit()
        return jsonify({"message": "Data saved to database"})
    except mysql.connector.Error as e:
        return "Error occurred while saving data to database"


# Create history table if not exists
cursor.execute("CREATE TABLE IF NOT EXISTS history (id INT AUTO_INCREMENT PRIMARY KEY, calculation VARCHAR(255))")
if __name__ == "__main__":
    app.run()