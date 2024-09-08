from flask import Flask, render_template, request, session, jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import plotly.graph_objs as go
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Load stock data from CSV (NSE and BSE)
def load_stock_data():
    stock_data = pd.read_csv('stocks.csv')
    return stock_data


# Generate simulated stock data
def generate_stock_data(stock_name):
    num_days = 100
    dates = [datetime.now() - timedelta(days=i) for i in range(num_days)]
    prices = np.random.uniform(low=100, high=500, size=num_days)
    volume = np.random.randint(low=1000, high=10000, size=num_days)
    return pd.DataFrame({'Date': dates, 'Price': prices, 'Volume': volume})


# Save stock chart as an image
def save_stock_chart(stock_name, stock_data):
    plt.figure(figsize=(10, 5))
    plt.plot(stock_data['Date'], stock_data['Price'], label=f'{stock_name} Price')
    plt.title(f'{stock_name} Stock Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    chart_path = f'static/chart_images/{stock_name}_chart.png'
    plt.savefig(chart_path)
    plt.close()
    return chart_path


# Home route
@app.route('/')
def home():
    return render_template('index.html')


# Search stock route
@app.route('/search', methods=['POST'])
def search_stock():
    stock_name = request.form['stock']
    stock_data = generate_stock_data(stock_name)
    chart_path = save_stock_chart(stock_name, stock_data)
    return render_template('stock.html', stock_name=stock_name, stock_data=stock_data.to_dict('records'), chart_path=chart_path)


# Autocomplete route for suggesting stocks based on user input
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')  # Get the query string parameter
    stock_data = load_stock_data()

    if search:
        # Filter stocks by the search string
        filtered_stocks = stock_data[
            stock_data['name'].str.contains(search, case=False, na=False) | 
            stock_data['symbol'].str.contains(search, case=False, na=False)
        ]

        # Convert filtered results to JSON format
        suggestions = filtered_stocks[['symbol', 'name']].to_dict(orient='records')
        return jsonify(suggestions)
    return jsonify([])  # Return empty list if no query is provided



# Buy stock route
@app.route('/buy', methods=['POST'])
def buy_stock():
    stock_name = request.form['stock']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    if 'portfolio' not in session:
        session['portfolio'] = []

    session['portfolio'].append({'stock': stock_name, 'price': price, 'quantity': quantity})
    return render_template('portfolio.html', portfolio=session['portfolio'])


# Sell stock route
@app.route('/sell', methods=['POST'])
def sell_stock():
    stock_name = request.form['stock']
    quantity = int(request.form['quantity'])

    session['portfolio'] = [trade for trade in session['portfolio'] if trade['stock'] != stock_name or trade['quantity'] < quantity]
    return render_template('portfolio.html', portfolio=session['portfolio'])



if __name__ == '__main__':
    app.run(debug=True)
