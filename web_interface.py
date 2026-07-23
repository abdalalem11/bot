from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
    <h1>🔥 Hack Bot Control Panel</h1>
    <p>Active Sessions: {{ sessions }}</p>
    <p>Bot Status: Running</p>
    """, sessions=0)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
