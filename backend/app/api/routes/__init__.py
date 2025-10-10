"""
API routes package for SubmitEZ.
"""

from .health_routes import health_bp
from .submission_routes import submission_bp

__all__ = [
    'health_bp',
    'submission_bp'
]