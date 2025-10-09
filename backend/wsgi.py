"""
SubmitEZ WSGI Entry Point for Production

This module provides the WSGI application for production deployment.
Use with Gunicorn, uWSGI, or other WSGI servers.

Usage with Gunicorn:
    gunicorn wsgi:app
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
    gunicorn --config gunicorn_config.py wsgi:app

Usage with uWSGI:
    uwsgi --http :5000 --wsgi-file wsgi.py --callable app
    
Environment Variables:
    FLASK_ENV - Should be set to 'production'
    All other config variables from .env
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.config import ProductionConfig

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Create the WSGI application
try:
    app = create_app('production')
    
    # Log startup information
    app.logger.info("SubmitEZ production server initialized")
    app.logger.info(f"Python version: {sys.version}")
    app.logger.info(f"Working directory: {os.getcwd()}")
    
except Exception as e:
    # Log error and re-raise
    print(f"Failed to initialize application: {e}", file=sys.stderr)
    raise


# WSGI application callable
application = app


def get_app():
    """
    Factory function to get application instance.
    Useful for some deployment platforms.
    """
    return app


if __name__ == '__main__':
    """
    Allow running with: python wsgi.py
    Though Gunicorn is recommended for production.
    """
    print("""
    ⚠️  WARNING: Running production server with Flask's built-in server.
    
    This is NOT recommended for production use!
    Use Gunicorn instead:
    
        gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
    
    Or with a configuration file:
    
        gunicorn --config gunicorn_config.py wsgi:app
    
    Press CTRL+C to quit, or continue at your own risk...
    """)
    
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nShutdown complete.")


# Optional: Gunicorn configuration (can be in separate gunicorn_config.py)
"""
Example gunicorn_config.py:

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "submitez"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"

# Server hooks
def on_starting(server):
    print("SubmitEZ server starting...")

def on_reload(server):
    print("SubmitEZ server reloading...")

def when_ready(server):
    print("SubmitEZ server ready to accept connections")

def on_exit(server):
    print("SubmitEZ server shutting down...")
"""