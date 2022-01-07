from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__)
app.secret_key = '231ad3242e231b2132b214034bbca3'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'next_bank'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/customers', methods = ['GET','POST'])
def customers():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customers")
    customer_details = cursor.fetchall()
    cursor.close()
    return render_template('/customers.html',customer_details = customer_details)

@app.route('/profile/<int:id>', methods = ['GET', 'POST'])
def user_profile(id):
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM customers where id = {id}")
    customer_profile = cursor.fetchone()
    cursor.close()
    return render_template('/profile.html',customer_profile = customer_profile)

@app.route('/transactions/<int:id>', methods = ['GET','POST'])
def transactions(id):
    failed_msg = ""
    success_msg = ""
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT id,Name,current_balance FROM customers where id = {id}")
    customer_info = cursor.fetchone()
    cursor.execute(f"SELECT id,Name,current_balance FROM customers where id!={id}")
    other_customers = cursor.fetchall()
    if request.method == "POST":
        try:
            transaction_details = request.form
            sender = transaction_details['sender']
            sender_balance = customer_info['current_balance']
            receiver = transaction_details['receiver']
            cursor.execute(f"SELECT id, Name, current_balance from customers where Name = '{receiver}'")
            receiver_info = cursor.fetchone()
            receiver_balance = receiver_info['current_balance']
            transfer_balance = int(transaction_details['balance'])
            if sender_balance < transfer_balance:
                failed_msg = "Insufficient Balance"
            elif transfer_balance < 0:
                failed_msg = "Please Enter a Valid Positive Value"
            else:
                date_time = datetime.now()
                updated_sender_balance = sender_balance - transfer_balance
                updated_receiver_balance = receiver_balance + transfer_balance
                # date_time = datetime.now()
                cursor.execute(f"UPDATE customers set current_balance = {updated_sender_balance} WHERE Name = '{sender}'")
                cursor.execute(f"UPDATE customers set current_balance = {updated_receiver_balance} WHERE Name = '{receiver}'")
                cursor.execute("INSERT INTO trans_hist(Sender,Receiver,trans_amount,Date) VALUES (%s,%s,%s,%s)",(sender,receiver,transfer_balance,date_time),)
                mysql.connection.commit()
                cursor.close()
                success_msg = "Transaction Successful"
        except ValueError as ve:
            failed_msg = "Please enter a valid value"
    return render_template('/transactions.html',customer_info = customer_info, other_customers = other_customers, failed_msg = failed_msg,success_msg = success_msg)

@app.route('/transaction-history')
def trans_hist():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM trans_hist")
    transaction_history = cursor.fetchall()
    if transaction_history:
        transaction_record = True
    else:
        transaction_record = False
    cursor.close()
    return render_template('trans_hist.html', transaction_history = transaction_history, transaction_record = transaction_record)

@app.route('/transaction-history/<string:name>')
def user_trans_hist(name):
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM trans_hist WHERE Sender = '{name}' OR Receiver = '{name}'")
    user_transaction_history = cursor.fetchall()
    if user_transaction_history:
        user_transaction = True
    else:
        user_transaction = False
    cursor.close()
    return render_template('user_trans_hist.html', user_transaction_history = user_transaction_history, user_transaction = user_transaction)

@app.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')

if __name__ == '__main__':
    app.run(debug=True)