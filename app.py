from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_input = request.json.get('input')
    response = get_ai_response(user_input)
    return jsonify({'response': response})

def get_ai_response(text):
    # Бесплатный API HuggingFace
    API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
    
    try:
        # Для моделей, не требующих API ключа
        payload = {"inputs": text}
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json().get('generated_text', 'Нет ответа')
        else:
            return f"Ошибка API: {response.status_code}"
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)