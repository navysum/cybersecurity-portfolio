import re
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Example Regex to find failed SSH logins
FAILED_LOGIN_PATTERN = r"Failed password for .* from (\d+\.\d+\.\d+\.\d+)"

@app.route('/api/logs')
def get_logs():
    data = {"failed_attempts": 0, "attacker_ips": []}
    
    # In a real scenario, you'd open /var/log/auth.log
    with open('mock_logs.txt', 'r') as f:
        for line in f:
            match = re.search(FAILED_LOGIN_PATTERN, line)
            if match:
                data["failed_attempts"] += 1
                data["attacker_ips"].append(match.group(1))
                
    return jsonify(data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)