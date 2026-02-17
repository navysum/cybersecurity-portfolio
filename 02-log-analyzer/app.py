from flask import Flask, jsonify, render_template

# 1. Initialize the app FIRST
app = Flask(__name__) 

# 2. THEN define the routes
@app.route('/api/logs')
def get_logs():
    # your logic here...
    return jsonify({"status": "working"})