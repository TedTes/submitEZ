"""
SubmitEZ Configuration Management

This module defines configuration classes for different environments.
Follows the Configuration Pattern for flexible deployment.
"""

import os
from typing import Set
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Application
    APP_NAME = 'SubmitEZ'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'submissions')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
    
    # Optional: Anthropic Claude
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/submitez-uploads')
    ALLOWED_EXTENSIONS: Set[str] = {'pdf', 'xlsx', 'xls', 'docx', 'doc'}
    
    # Processing Configuration
    EXTRACTION_TIMEOUT = int(os.getenv('EXTRACTION_TIMEOUT', '300'))  # 5 minutes
    GENERATION_TIMEOUT = int(os.getenv('GENERATION_TIMEOUT', '180'))  # 3 minutes
    VALIDATION_TIMEOUT = int(os.getenv('VALIDATION_TIMEOUT', '60'))   # 1 minute
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = False
    TESTING = False
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration values."""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_vars)}. "
                f"Please check your .env file."
            )


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    ENV = 'development'
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    
    # Relaxed timeouts for debugging
    EXTRACTION_TIMEOUT = 600  # 10 minutes
    GENERATION_TIMEOUT = 300  # 5 minutes


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    ENV = 'production'
    
    # Strict configuration for production
    LOG_LEVEL = 'WARNING'
    
    # Must have strong secret key in production
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Validate secret key strength in production
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError(
                "SECRET_KEY must be changed in production! "
                "Generate a secure key with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    
    # Use test database and storage
    SUPABASE_BUCKET = 'test-submissions'
    
    # Faster timeouts for tests
    EXTRACTION_TIMEOUT = 30
    GENERATION_TIMEOUT = 20
    VALIDATION_TIMEOUT = 5
    
    # Disable external API calls in tests (can be mocked)
    TESTING_MODE = True


class StagingConfig(ProductionConfig):
    """Staging environment configuration (pre-production)."""
    
    ENV = 'staging'
    DEBUG = False
    
    # Staging-specific settings
    LOG_LEVEL = 'INFO'


# Configuration dictionary for easy access
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name: str = None) -> Config:
    """
    Get configuration class for specified environment.
    
    Args:
        env_name: Environment name (development, production, testing, staging)
        
    Returns:
        Configuration class instance
    """
    if env_name is None:
        env_name = os.getenv('FLASK_ENV', 'development')
    
    return config_by_name.get(env_name.lower(), DevelopmentConfig)