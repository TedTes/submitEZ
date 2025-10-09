"""
SubmitEZ Development Server Entry Point

This script runs the Flask development server.
For production, use wsgi.py with Gunicorn instead.

Usage:
    python run.py
    
Environment Variables:
    FLASK_ENV - Set to 'development' or 'production' (default: development)
    FLASK_HOST - Host to bind to (default: 0.0.0.0)
    FLASK_PORT - Port to bind to (default: 5000)
    FLASK_DEBUG - Enable debug mode (default: True in development)
"""

import os
import sys
from app import create_app
from app.config import config_by_name

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def main():
    """Run the development server."""
    
    # Get environment configuration
    env = os.getenv('FLASK_ENV', 'development')
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    # Create application instance
    try:
        app = create_app(env)
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Failed to create application: {e}\n", file=sys.stderr)
        sys.exit(1)
    
    # Print startup banner
    print_banner(app, host, port, env)
    
    # Run development server
    try:
        app.run(
            host=host,
            port=port,
            debug=app.config['DEBUG'],
            use_reloader=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Server error: {e}\n", file=sys.stderr)
        sys.exit(1)


def print_banner(app, host, port, env):
    """Print startup information banner."""
    
    # Color codes for terminal
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    # Environment color
    env_color = GREEN if env == 'development' else YELLOW if env == 'staging' else RED
    
    # Banner
    print(f"""
{BLUE}{BOLD}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           {END}{BOLD}SubmitEZ API Server{END}{BLUE}{BOLD}                         ║
║     {END}Commercial Insurance Submission Automation{BLUE}{BOLD}        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝{END}

{BOLD}Environment:{END} {env_color}{env.upper()}{END}
{BOLD}Debug Mode:{END}  {'✓ Enabled' if app.config['DEBUG'] else '✗ Disabled'}

{BOLD}🌐 Server:{END}
   Local:    http://localhost:{port}
   Network:  http://{host}:{port}

{BOLD}📡 Endpoints:{END}
   Health:   http://localhost:{port}/health
   Root:     http://localhost:{port}/
   API:      http://localhost:{port}/api/

{BOLD}📦 Configuration:{END}
   Upload Limit:     {app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024):.0f}MB
   Allowed Files:    {', '.join(app.config['ALLOWED_EXTENSIONS'])}
   Extraction:       {app.config['EXTRACTION_TIMEOUT']}s timeout
   Generation:       {app.config['GENERATION_TIMEOUT']}s timeout

{BOLD}🔧 Database:{END}
   Supabase:         {'✓ Configured' if app.config['SUPABASE_URL'] else '✗ Not configured'}
   Storage Bucket:   {app.config['SUPABASE_BUCKET']}

{BOLD}🤖 AI Services:{END}
   OpenAI:           {'✓ Configured' if app.config['OPENAI_API_KEY'] else '✗ Not configured'}
   Model:            {app.config['OPENAI_MODEL']}

{GREEN}{BOLD}🚀 Server starting...{END}
{YELLOW}Press CTRL+C to quit{END}
""")


def check_dependencies():
    """Check if required dependencies are installed."""
    
    required_packages = [
        'flask',
        'flask_cors',
        'supabase',
        'openai',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt\n")
        sys.exit(1)


if __name__ == '__main__':
    # Check dependencies before starting
    check_dependencies()
    
    # Run the server
    main()