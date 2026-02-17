import os

@app.route('/api/logs')
def get_logs():
    processed_path = './logs/processed'
    all_threats = []
    
    # Python reads every "cleaned" file Java created
    for filename in os.listdir(processed_path):
        with open(os.path.join(processed_path, filename), 'r') as f:
            # Your regex parsing logic here...
            pass