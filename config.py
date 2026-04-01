"""
Production configuration for Paris Subventions API
Supports environment variables for flexible deployment
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Server settings
    PORT = int(os.environ.get('PORT', 8010))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    # Data file path (configurable for different environments)
    DATA_FILE = os.environ.get('DATA_FILE', '/home/openclaw/.openclaw/workspace/paris-assos-website/data_net.json')
    
    # Static files
    STATIC_FOLDER = os.environ.get('STATIC_FOLDER', '/home/openclaw/.openclaw/workspace/paris-assos-website')
    
    # Caching settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))  # 5 minutes default
    CACHE_THRESHOLD = int(os.environ.get('CACHE_THRESHOLD', 1000))  # Max items in cache
    
    # API settings
    DEFAULT_PER_PAGE = int(os.environ.get('DEFAULT_PER_PAGE', 50))
    MAX_PER_PAGE = int(os.environ.get('MAX_PER_PAGE', 100))
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Security
    RATE_LIMIT = os.environ.get('RATE_LIMIT', '100 per minute')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    CACHE_TYPE = 'SimpleCache'  # Use SimpleCache for Render/Railway (no Redis needed)
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    LOG_LEVEL = 'WARNING'
    
    # In production, require explicit origins
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')  # Can be restricted in env

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 60  # 1 minute for dev
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    CACHE_TYPE = 'NullCache'  # No caching in tests
    DATA_FILE = os.environ.get('TEST_DATA_FILE', '/tmp/test_data.json')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}

def get_config():
    """Get current configuration based on FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'production')
    return config.get(env, ProductionConfig)()