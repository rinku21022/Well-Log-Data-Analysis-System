# from flask import Flask
# from flask_cors import CORS
# from flask_migrate import Migrate
# from flask import send_from_directory
# from dotenv import load_dotenv
# import os

# from models import db

# # Load environment variables with explicit path
# basedir = os.path.abspath(os.path.dirname(__file__))
# dotenv_path = os.path.join(basedir, '.env')
# load_dotenv(dotenv_path)
# print(f"DEBUG: Loaded .env from: {dotenv_path}")
# print(f"DEBUG: GEMINI_API_KEY = {'SET (' + str(len(os.getenv('GEMINI_API_KEY', ''))) + ' chars)' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")

# app = Flask(__name__)
# CORS(app)

# # Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
# app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# # Initialize extensions
# db.init_app(app)
# migrate = Migrate(app, db)

# # Import routes
# from routes import upload_routes, file_routes, visualization_routes, ai_routes

# # Register blueprints
# app.register_blueprint(upload_routes.bp)
# app.register_blueprint(file_routes.bp)
# app.register_blueprint(visualization_routes.bp)
# app.register_blueprint(ai_routes.bp)

# @app.route('/')
# def index():
#     return {
#         'message': 'Well-Log Analysis API',
#         'version': '1.0',
#         'endpoints': {
#             'upload': '/api/upload',
#             'files': '/api/files',
#             'visualize': '/api/visualize',
#             'interpret': '/api/interpret',
#             'chat': '/api/chat'
#         }
#     }

# @app.route('/health')
# def health():
#     return {'status': 'healthy'}

# @app.route('/files/<path:filepath>')
# def serve_uploaded_file(filepath):
#     """Serve uploaded LAS files"""
#     uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
#     return send_from_directory(uploads_dir, filepath)

# if __name__ == '__main__':
#     port = int(os.getenv('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask import send_from_directory
from dotenv import load_dotenv
import os

from models import db

# Load environment variables with explicit path
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path)
print(f"DEBUG: Loaded .env from: {dotenv_path}")
print(f"DEBUG: GEMINI_API_KEY = {'SET (' + str(len(os.getenv('GEMINI_API_KEY', ''))) + ' chars)' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Import routes
from routes import upload_routes, file_routes, visualization_routes, ai_routes

# Register blueprints
app.register_blueprint(upload_routes.bp)
app.register_blueprint(file_routes.bp)
app.register_blueprint(visualization_routes.bp)
app.register_blueprint(ai_routes.bp)

@app.route('/')
def index():
    return {
        'message': 'Well-Log Analysis API',
        'version': '1.0',
        'endpoints': {
            'upload': '/api/upload',
            'files': '/api/files',
            'visualize': '/api/visualize',
            'interpret': '/api/interpret',
            'chat': '/api/chat'
        }
    }

@app.route('/health')
def health():
    return {'status': 'healthy'}

@app.route('/files/<path:filepath>')
def serve_uploaded_file(filepath):
    """Serve uploaded LAS files"""
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    return send_from_directory(uploads_dir, filepath)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
