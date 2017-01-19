# -*- coding: utf-8 -*-
from functools import wraps

from flask import current_app
from flask import request
from flask.ext.login import current_user

from settings import config


def admin_required(func):
    """
    Ensures that the current user: 
        is logged in and 
        is authenticated and 
        is ADMIN 
    before calling the actual view. 
    
    :param func: The view function to decorate.
    :type func: function
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not (current_user.is_authenticated and current_user.is_admin):
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view


def access_token_required(func):
    """
    Works for API internal calls with ACESS_TOKEN provided as a HTTP Header.
    Just like @login_required, but for the API calls.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)

        if not access_token_in_headers():
            return current_app.login_manager.unauthorized()

        return func(*args, **kwargs)

    return decorated_view


def auth_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # Debug Mode with "No Login"
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)

        # Login
        if current_user.is_authenticated:
            return func(*args, **kwargs)

        # Access token
        if access_token_in_headers():
            return func(*args, **kwargs)

        return current_app.login_manager.unauthorized()
    return decorated_view


def access_token_in_headers():
    token = request.headers.get('ACCESS-TOKEN')
    if not token:
        current_app.logger.debug(u'Access token is not passed in request header "ACCESS-TOKEN".')
        return False

    token_is_valid = config.ACCESS_TOKEN == token
    if not token_is_valid:
        current_app.logger.debug(u'Access token is invalid. Needed "{}", got "{}".'.format(
            config.ACCESS_TOKEN,
            token
        ))
        return False

    return True
