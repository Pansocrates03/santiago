import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
from collections import Counter
import io
from flask import Flask, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

customer_id = "66e601899683f20dd5189be2"
account = "66e601899683f20dd5189be2"

def get_accounts(cust_id):
    url_ = 'http://api.nessieisreal.com/customers/{}/accounts?key=ca48cfabf9e384486beb873e84037309'.format(cust_id)
    response = requests.get(url_)
    deposits_data = json.loads(response.text)
    return pd.DataFrame(deposits_data)

def get_purch_acc(acc_id):
    url_ = 'http://api.nessieisreal.com/accounts/{}/purchases?key=ca48cfabf9e384486beb873e84037309'.format(acc_id)
    response = requests.get(url_)
    deposits_data = json.loads(response.text)
    return pd.DataFrame(deposits_data)

def get_dep_acc(acc_id):
    url_ = 'http://api.nessieisreal.com/accounts/{}/deposits?key=ca48cfabf9e384486beb873e84037309'.format(acc_id)
    response = requests.get(url_)
    deposits_data = json.loads(response.text)
    return pd.DataFrame(deposits_data)

def get_merch(merch_id):
    url_ = 'http://api.nessieisreal.com/merchants/{}?key=ca48cfabf9e384486beb873e84037309'.format(merch_id)
    response = requests.get(url_)
    return json.loads(response.text)

def get_merch_name(merch_id):
    return get_merch(merch_id)['name']

def add_merch_name(df):
    df['merchant_name'] = df['merchant_id'].apply(get_merch_name)
    return df

@app.route('/chart/cumulative_spending', methods=['GET'])
def get_cumulative_spending_chart():
    table_acc = get_accounts(customer_id)
    purch_acc = get_purch_acc(table_acc['_id'][2])
    purch_acc = purch_acc.sort_values(by='purchase_date', key=pd.to_datetime)
    purch_acc.reset_index(drop=True, inplace=True)

    purch_acc['cumulative_amount'] = purch_acc['amount'].cumsum()
    plt.figure(figsize=(12, 8))
    plt.plot(purch_acc.index, purch_acc['cumulative_amount'], marker='o', color='#004878', linestyle='-', linewidth=2)
    plt.xlabel('Transaction Order', fontsize=14)
    plt.ylabel('Cumulative Amount', fontsize=14)
    plt.title('Cumulative Spending Over Time', fontsize=16, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300)
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')

@app.route('/chart/spending_by_merchant', methods=['GET'])
def get_spending_by_merchant_chart():
    table_acc = get_accounts(customer_id)
    purch_acc = get_purch_acc(table_acc['_id'][2])
    purch_acc = add_merch_name(purch_acc)

    trends = purch_acc.groupby('merchant_name').sum()['amount']
    trends_sorted = trends.sort_values(ascending=False)
    
    plt.figure(figsize=(12, 8))
    trends_sorted.plot(kind='bar', color='#004878', edgecolor='#D22E1E')
    plt.xlabel('Merchant Name', fontsize=14)
    plt.ylabel('Total Amount', fontsize=14)
    plt.title('Spending by Merchant', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300)
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')

@app.route('/chart/purchase_frequency_by_merchant', methods=['GET'])
def get_purchase_frequency_by_merchant_chart():
    table_acc = get_accounts(customer_id)
    purch_acc = get_purch_acc(table_acc['_id'][2])
    purch_acc = add_merch_name(purch_acc)

    trends = purch_acc.groupby('merchant_name').count()['amount']
    trends_sorted = trends.sort_values(ascending=False)
    
    plt.figure(figsize=(12, 8))
    trends_sorted.plot(kind='bar', color='#004878', edgecolor='#D22E1E')
    plt.xlabel('Merchant Name', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.title('Purchase Trends', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300)
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')

@app.route('/chart/category_count', methods=['GET'])
def get_category_count_chart():
    table_acc = get_accounts(customer_id)
    purch_acc = get_purch_acc(table_acc['_id'][2])

    categorias = get_cat(purch_acc)
    contador_categorias = Counter(categorias)
    categorias_ordenadas = contador_categorias.most_common()

    categorias, conteos = zip(*categorias_ordenadas)

    plt.figure(figsize=(12, 8))
    plt.bar(categorias, conteos, color='#004878', edgecolor='#D22E1E')
    plt.xlabel('Categorías', fontsize=14)
    plt.ylabel('Conteo', fontsize=14)
    plt.title('Conteo de Categorías', fontsize=16, fontweight='bold')
    plt.xticks(rotation=90)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300)
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')

@app.route('/chart/cumulative_balance', methods=['GET'])
def get_cumulative_balance_chart():
    table_acc = get_accounts(customer_id)
    purch_acc = get_purch_acc(table_acc['_id'][2])
    dep_acc = get_dep_acc(table_acc['_id'][2])

    expenses_df = purch_acc[['purchase_date', 'amount']].rename(columns={'purchase_date': 'date'})
    expenses_df['type'] = 'expense'

    income_df = dep_acc[['transaction_date', 'amount']].rename(columns={'transaction_date': 'date'})
    income_df['type'] = 'income'

    combined_df = pd.concat([expenses_df, income_df], ignore_index=True)
    combined_df = combined_df.reset_index(drop=True)
    combined_df['amount'] = combined_df.apply(lambda row: -row['amount'] if row['type'] == 'expense' else row['amount'], axis=1)
    combined_df['cumulative_balance'] = 10000 + combined_df['amount'].cumsum()

    plt.figure(figsize=(14, 8))
    plt.plot(combined_df.index, combined_df['cumulative_balance'], color='#004878', label='Cumulative Balance', linewidth=2)
    plt.scatter(combined_df[combined_df['type'] == 'expense'].index, combined_df[combined_df['type'] == 'expense']['cumulative_balance'], color='#D22E1E', label='Expenses')
    plt.scatter(combined_df[combined_df['type'] == 'income'].index, combined_df[combined_df['type'] == 'income']['cumulative_balance'], color='#004878', label='Income')
    
    plt.xlabel('Transaction Order', fontsize=14)
    plt.ylabel('Cumulative Balance', fontsize=14)
    plt.title('Cumulative Balance Over Time', fontsize=16, fontweight='bold')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300)
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
