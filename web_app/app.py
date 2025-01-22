# File 2: app.py
from flask import Flask, jsonify, request, render_template
from test_session import TestSession
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sessions', methods=['POST'])
def create_session():
    if TestSession.get_current_session():
        return jsonify({'error': 'Test already running'}), 400
        
    data = request.json
    name = data.get('name')
    config = data.get('config')
    
    if not name or not config:
        return jsonify({'error': 'Missing parameters'}), 400
    
    if TestSession.start_session(name, config):
        return jsonify({'message': 'Test started', 'name': name})
    return jsonify({'error': 'Failed to start test'}), 500

@app.route('/api/sessions/current', methods=['DELETE'])
def kill_session():
    if TestSession.stop_session():
        return jsonify({'message': 'Test stopped'})
    return jsonify({'error': 'No test running'}), 404

@app.route('/api/sessions/current', methods=['GET'])
def get_current_session():
    session = TestSession.get_current_session()
    if session:
        return jsonify(session.get_state())
    return jsonify({'error': 'No active session'}), 404

@app.route('/api/sessions/archived', methods=['GET'])
def get_archived_sessions():
    sessions = []
    for fname in os.listdir('sessions'):
        if fname.endswith('.json'):
            sessions.append(fname[:-5])
    return jsonify(sessions)

@app.route('/api/sessions/archived/<name>', methods=['GET'])
def get_archived_session(name):
    try:
        with open(f'sessions/{name}.json') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    os.makedirs('sessions', exist_ok=True)
    app.run(debug=True, port=5001)