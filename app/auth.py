#!/usr/bin/python3
"""Define authentication-related API routes"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
import json
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .models import User
from .forms import RegistrationForm, LoginForm
from .verified import send_confirmation_email, confirm_token
from .extensions import db
from .routes import api

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():

    return render_template('index.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email is already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        send_confirmation_email(new_user.email)
        flash('A confirmation email has been sent via email. Please check your inbox and spam folder.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@api.route('/confirm/<token>')
def confirm_email(token):
    """Confirm user's email using the token"""
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.email_confirmed = True
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.email_confirmed:
                flash('Please confirm your email to login.', 'error')
                return redirect(url_for('auth.login'))
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('api.home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success') 
    return redirect(url_for('auth.index'))
