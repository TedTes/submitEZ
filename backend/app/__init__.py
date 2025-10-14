"""
SubmitEZ Flask Application Factory

This module implements the Application Factory pattern for creating
Flask application instances with different configurations.

Benefits:
- Multiple app instances with different configs (dev, test, prod)
- Easier testing with isolated app contexts
- Cleaner organization with blueprints
- Delayed initialization of extensions
"""

from flask import Flask, jsonify
from flask_cors import CORS
from app.config import config_by_name, Config


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function.
    
    Args:
        config_name: Configuration to use ('development', 'production', 'testing')
        
    Returns:
        Configured Flask application instance
        
    Example:
        >>> app = create_app('development')
        >>> app.run()
    """
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        import os
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_class = config_by_name.get(config_name.lower(), config_by_name['default'])
    app.config.from_object(config_class)
    
    # Validate configuration
    try:
        config_class.validate_config()
    except ValueError as e:
        app.logger.error(f"Configuration validation failed: {e}")
        raise
    
    # Initialize configuration
    config_class.init_app(app)
    
    # Initialize extensions
    _initialize_extensions(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register shell context
    _register_shell_context(app)
    
    # Setup logging
    _setup_logging(app)
    
    # Log startup info
    app.logger.info(f"SubmitEZ initialized in {config_name} mode")
    
    return app


def _initialize_extensions(app: Flask):
    """Initialize Flask extensions."""
    
    # CORS - Allow frontend to make requests
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         expose_headers=['Content-Type', 'X-Request-ID'],
         allow_headers=['Content-Type', 'Authorization', 'X-Request-ID',
             'X-Request-Time',
             'Accept',
             'Origin',
             'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])
    


def _register_blueprints(app: Flask):
    """Register Flask blueprints for routes."""
    
    # Import blueprints here to avoid circular imports
    from app.api.routes.health_routes import health_bp
    from app.api.routes.submission_routes import submission_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(submission_bp)
    
    # Health check route (inline for now)
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': app.config['APP_NAME'],
            'environment': app.config['ENV'],
            'version': '1.0.0'
        }), 200
    
    @app.route('/')
    def index():
        """Root endpoint."""
        return jsonify({
            'message': f"Welcome to {app.config['APP_NAME']} API",
            'version': '1.0.0',
            'documentation': '/api/docs',
            'health': '/health'
        }), 200


def _register_error_handlers(app: Flask):
    """Register global error handlers."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        app.logger.error(f'Internal server error: {error}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle file upload size limit errors."""
        return jsonify({
            'error': 'File Too Large',
            'message': f'File size exceeds {app.config["MAX_CONTENT_LENGTH"] / (1024 * 1024)}MB limit',
            'status_code': 413
        }), 413


def _register_shell_context(app: Flask):
    """Register shell context for Flask CLI."""
    
    @app.shell_context_processor
    def make_shell_context():
        """Make objects available in Flask shell."""
        return {
            'app': app,
            'config': app.config
        }


def _setup_logging(app: Flask):
    """Setup application logging."""
    
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    
    # Only setup file logging in production
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup rotating file handler
        file_handler = RotatingFileHandler(
            'logs/submitez.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            app.config['LOG_FORMAT']
        ))
        
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)
    
    # Set log level
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    app.logger.info(f"{app.config['APP_NAME']} startup")


# Create default application instance for imports
app = create_app()