# -*- coding: utf-8 -*-
"""Application configuration."""
import os

from pump_select.utils import get_env_or_fail


class ProdConfig(object):
    """Base configuration."""

    SECRET_KEY = get_env_or_fail('PUMP_SELECT_SECRET')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Production configuration.
    ENV = 'prod'


class DevConfig(ProdConfig):
    # Development configuration.
    ENV = 'dev'
    DEBUG = True
    DEBUG_TB_ENABLED = True
    WERKZEUG_DEBUG_PIN = 'off'
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    SQLALCHEMY_DATABASE_URI = os.environ.get('PUMP_SELECT_DATABASE_URI')


class TestConfig(ProdConfig):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing


config = DevConfig if os.environ.get('FLASK_DEBUG') == '1' else ProdConfig
