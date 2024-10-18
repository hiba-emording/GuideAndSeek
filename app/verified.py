#!/usr/bin/python3
"""Utility functions for email verification"""
from flask import url_for, current_app, render_template
from itsdangerous import URLSafeTimedSerializer
from .mail import send_email


def generate_confirmation_token(email):
    """
    Generate a confirmation token for email verification.
    
    :param email: User's email address.
    :return: Token string.
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    """
    Confirm the validity of the token.
    
    :param token: Token string.
    :param expiration: Expiration time in seconds.
    :return: Email if token is valid, else None.
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email


def send_confirmation_email(to_email):
    """
    Send a confirmation email to the user.
    
    :param to_email: Recipient email address.
    """
    token = generate_confirmation_token(to_email)
    confirm_url = url_for('api.confirm_email', token=token, _external=True)
    html = render_template('activate.html', confirm_url=confirm_url)
    text = """"
        Welcome! Thanks for signing up. Please follow this link to activate your account:
        {}
        Thanks
        """.format(confirm_url)

    is_sent = send_email(to_email, 'Confirm Your Email Address', text, html)
    if not is_sent:
        current_app.logger.error('Failed to send confirmation email.')

