import os
import sys
sys.path.append(os.getcwd())
from dotenv import load_dotenv
load_dotenv()
from app import create_app

if __name__ == "__main__":
    os.environ['FLASK_ENV'] = 'development'
    app = create_app()
    print("Starting Debug Server on 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)
