from flask import Flask
from . import routes

def create_app():
    """
    Create and configure the Flask application
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(routes.api_blueprint, url_prefix='/api')
    
    # Add a simple index route
    @app.route('/')
    def index():
        return "RSS Social Bot API - Use the /api endpoints with X-Config headers to customize behavior"
    
    return app

# For running with Flask development server
app = create_app()

if __name__ == "__main__":
    # Only for development
    app.run(debug=True, host='0.0.0.0', port=5000)
