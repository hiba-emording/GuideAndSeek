#!/usr/bin/python3
"""Define authentication-related API routes"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
import json
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .models import User
from .forms import RegistrationForm, LoginForm
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
        # Check if user already exists
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email is already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Create new user and add to the database
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
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
