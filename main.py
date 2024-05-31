from flask import Flask, request, jsonify, render_template
import requests
import random
import time
import threading
from bs4 import BeautifulSoup

app = Flask(__name__)
proxies = []

# Read proxies from file
with open('proxies.txt', 'r') as file:
    proxies = [line.strip() for line in file.readlines()]

current_proxy = None
website_to_check = None

def fetch_website():
    global current_proxy, website_to_check
    while True:
        if website_to_check:
            current_proxy = random.choice(proxies)
            proxy_dict = {
                'http': f'http://{current_proxy}',
                'https': f'https://{current_proxy}',
            }
            try:
                response = requests.get(website_to_check, proxies=proxy_dict)
                soup = BeautifulSoup(response.content, 'html.parser')
                status = f'Checked {website_to_check} using {current_proxy} - Status: {response.status_code}'
                print(status)
                with app.app_context():
                    app.logger.info(status)
            except Exception as e:
                status = f'Error with {current_proxy} - {str(e)}'
                print(status)
                with app.app_context():
                    app.logger.error(status)
        time.sleep(15)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global website_to_check
    data = request.get_json()
    website_to_check = data.get('website')
    return jsonify({'message': f'Started checking {website_to_check}'})

@app.route('/events')
def events():
    def generate():
        with app.logger as logger:
            while True:
                message = logger.get_message()
                if message:
                    yield f'data: {message}\n\n'
                time.sleep(1)

    return app.response_class(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    threading.Thread(target=fetch_website, daemon=True).start()
    app.run(host='0.0.0.0', port=5000) 