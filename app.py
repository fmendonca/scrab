from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from tasks import generate_pdf_task
from celery.result import AsyncResult
import os

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/generate', methods=['POST'])
def generate():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    task = generate_pdf_task.delay(url)
    return jsonify({"task_id": task.id}), 202

@app.route('/status/<task_id>', methods=['GET'])
def status(task_id):
    result = AsyncResult(task_id)
    if result.state == 'PENDING':
        return jsonify({"state": "PENDING"})
    elif result.state == 'SUCCESS':
        return jsonify({"state": "SUCCESS", "pdf": result.result['pdf_path']})
    elif result.state == 'FAILURE':
        return jsonify({"state": "FAILURE", "error": str(result.info)})
    else:
        return jsonify({"state": result.state})
