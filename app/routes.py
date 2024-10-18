#!/usr/bin/python3
"""Define other API routes"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .models import User, Review, Availability, Appointment
from .forms import ProfileEditForm, AvailabilityForm, ReviewForm, AppointmentForm
from .extensions import db, socketio
from flask_socketio import emit
from datetime import datetime, timedelta, timezone
import pytz
from pytz import timezone
from dateutil import parser
import json
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError


api = Blueprint('api', __name__)

@api.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    next_appointment = get_next_appointment()

    if current_user.role == 'student':
        query = User.query.filter_by(role='teacher')
        query = query.join(Availability).filter(Availability.teacher_id == User.id).distinct()
        suggested_teachers, message = get_suggested_teachers(current_user.subject)

        filters = {
            'level': request.args.get('level'),
            'subject': request.args.get('subject'),
            'country': request.args.get('country')
        }

        if filters['level']:
            query = query.filter(User.level == filters['level'])
        if filters['subject']:
            query = query.filter(User.subject.ilike(f"%{filters['subject']}%"))
        if filters['country']:
            query = query.filter(User.country.ilike(f"%{filters['country']}%"))

        page = request.args.get('page', 1, type=int)
        paginated_teachers = query.paginate(page=page, per_page=5, error_out=False)

        return render_template('student_home.html',
                               suggested_teachers=suggested_teachers,
                               message=message,
                               teachers=paginated_teachers,
                               next_appointment=next_appointment,
                               filters=filters)

    elif current_user.role == 'teacher':
        form = AvailabilityForm()
        if form.validate_on_submit():
            new_availability = Availability(
                teacher_id=current_user.id,
                day_of_week=form.day_of_week.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data
            )
            db.session.add(new_availability)
            db.session.commit()
            flash('Availability added successfully!')
            return redirect(url_for('api.home'))

        availabilities = Availability.query.filter_by(teacher_id=current_user.id).all()
        pending_requests = Appointment.query.filter_by(teacher_id=current_user.id, status=Appointment.PENDING).all()

        if request.method == 'POST':
            appointment_id = request.form.get('appointment_id')
            action = request.form.get('action')

            appointment = Appointment.query.get(appointment_id)

            try:
                if action == 'accept':
                    appointment.status = Appointment.CONFIRMED
                    other_requests = Appointment.query.filter_by(
                        teacher_id=appointment.teacher_id,
                        slot_time=appointment.slot_time,
                        status=Appointment.PENDING
                    ).all()

                    for other_request in other_requests:
                        if other_request.id != appointment.id:
                            other_request.status = Appointment.DECLINED
                            other_request.cancel_reason = "Automatically declined due to another booking."

                    db.session.commit()

                    socketio.emit('appointment_confirmation', {
                        'student_id': appointment.student_id,
                        'teacher_name': current_user.username,
                        'appointment_title': appointment.title,
                        'appointment_time': appointment.slot_time.isoformat(),
                    }, namespace='/notifications')

                    flash('Appointment confirmed. Other overlapping requests have been declined.')

                elif action == 'decline':
                    appointment.status = Appointment.DECLINED
                    appointment.cancel_reason = "Appointment declined by the teacher."
                    db.session.commit()
                    flash('Appointment declined successfully.')

            except IntegrityError:
                db.session.rollback()
                flash('An error occurred while processing the appointment. Please try again.')

        return render_template('teacher_home.html', form=form, availabilities=availabilities, appointment_details=pending_requests, next_appointment=next_appointment, user=current_user)


@api.route('/list_teachers', methods=['GET'])
@login_required
def list_teachers():
    filters = {
        'level': request.args.get('level'),
        'subject': request.args.get('subject'),
        'country': request.args.get('country')
    }

    query = User.query.filter_by(role='teacher')
    query = query.join(Availability).filter(Availability.teacher_id == User.id).distinct()

    if filters['level']:
        query = query.filter(User.level == filters['level'])
    if filters['subject']:
        query = query.filter(User.subject.ilike(f"%{filters['subject']}%"))
    if filters['country']:
        query = query.filter(User.country.ilike(f"%{filters['country']}%"))

    page = request.args.get('page', 1, type=int)
    paginated_teachers = query.paginate(page=page, per_page=5, error_out=False)

    return render_template('student_home.html', teachers=paginated_teachers, filters=filters)


@api.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    profile_form = ProfileEditForm(obj=user)
    review_form = ReviewForm()

    if request.method == 'POST' and current_user.id == user.id:
        if profile_form.validate_on_submit():
            user.bio = profile_form.bio.data
            user.profile_picture = profile_form.profile_picture.data
            user.country = profile_form.country.data
            user.timezone = profile_form.timezone.data
            user.level = profile_form.level.data

            selected_subjects = request.form.getlist('subject')  
            user.subject = ','.join(selected_subjects)

            db.session.commit()
            flash('Profile updated successfully.')
            return redirect(url_for('api.view_profile', user_id=user.id))

    user_subjects = user.subject.split(',') if user.subject else []

    if review_form.validate_on_submit():
        new_review = Review(
            teacher_id=user.id,
            student_id=current_user.id,
            rating=review_form.rating.data,
            comment=review_form.comment.data
        )
        db.session.add(new_review)
        db.session.commit()
        flash('Review submitted successfully.')
        return redirect(url_for('api.view_profile', user_id=user.id))

    reviews = Review.query.filter_by(teacher_id=user.id).paginate(per_page=5)

    return render_template(
        'profile.html', 
        user=user, 
        profile_form=profile_form, 
        reviews=reviews, 
        review_form=review_form, 
        user_subjects=user_subjects
    )


@api.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileEditForm(obj=current_user)
    if current_user.subject:
        form.subject.data = current_user.subject.split(',')
    if current_user.country:
        form.country.data = current_user.country
    if current_user.time_zone:
        form.timezone.data = current_user.time_zone

    with open('app/static/data/countries.json') as f:
        countries = json.load(f)

    with open('app/static/data/subjects.json') as f:
        subjects = json.load(f)

    timezones = pytz.all_timezones

    form.country.choices = [(country, country) for country in countries]
    form.subject.choices = [(subject, subject) for subject in subjects]

    if form.validate_on_submit():
        current_user.bio = form.bio.data
        current_user.profile_picture = form.profile_picture.data
        current_user.country = form.country.data
        current_user.time_zone = form.timezone.data
        current_user.level = form.level.data

        selected_subjects = request.form.getlist('subject')
        current_user.subject = ','.join(selected_subjects)

        db.session.commit()

        flash('Your profile has been updated!', 'success')
        return redirect(url_for('api.view_profile', user_id=current_user.id))

    return render_template('edit_profile.html', 
                           profile_form=form,
                           countries=countries, 
                           subjects=subjects, 
                           timezones=timezones)


@api.route('/leave_review/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def leave_review(teacher_id):
    teacher = User.query.get_or_404(teacher_id)
    review_form = ReviewForm()

    if review_form.validate_on_submit():
        new_review = Review(
            teacher_id=teacher.id,
            student_id=current_user.id,
            rating=review_form.rating.data,
            comment=review_form.comment.data
        )
        db.session.add(new_review)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': 'Review submitted successfully!'})

        socketio.emit('new_review', {
            'teacher_id': teacher.id,
            'message': f"You received a new review from {current_user.username}."
        }, namespace='/notifications')

        flash('Review submitted successfully.')
        return redirect(url_for('api.view_profile', user_id=teacher.id))

    return render_template('view_profile.html', form=review_form, teacher=teacher)


@api.route('/teacher/availability', methods=['GET', 'POST'])
@login_required
def set_availability():
    if current_user.role != 'teacher':
        return redirect(url_for('api.home'))

    if not current_user.time_zone:
        flash('Please set your time zone in your profile before setting availability.', 'warning')
        return redirect(url_for('api.edit_profile'))

    availability_id = request.args.get('availability_id')
    today = datetime.now(pytz.timezone(current_user.time_zone)).weekday()
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    if availability_id:
        availability = Availability.query.get_or_404(availability_id)
        if availability.teacher_id != current_user.id:
            flash('Unauthorized access.')
            return redirect(url_for('api.set_availability'))
        form = AvailabilityForm(obj=availability)
    else:
        form = AvailabilityForm()

    if form.validate_on_submit():
        selected_day = days_of_week.index(form.day_of_week.data)
        now_in_teacher_tz = datetime.now(pytz.timezone(current_user.time_zone))

        if selected_day < today or (selected_day == today and form.start_time.data < now_in_teacher_tz.time()):
            flash('You cannot set availability for past times or days.', 'error')
            return redirect(url_for('api.set_availability'))
        if availability_id:
            availability.day_of_week = form.day_of_week.data
            availability.start_time = form.start_time.data
            availability.end_time = form.end_time.data
            db.session.commit()
            flash('Availability updated successfully!')
        else:
            add_availability(form, current_user.id)
            flash('Availability added successfully!')
        return redirect(url_for('api.set_availability'))

    availabilities = Availability.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher_home.html', form=form, availabilities=availabilities)


def add_availability(form, teacher_id):
    """Add availability for a teacher"""
    new_availability = Availability(
        teacher_id=teacher_id,
        day_of_week=form.day_of_week.data,
        start_time=form.start_time.data,
        end_time=form.end_time.data
    )
    db.session.add(new_availability)
    db.session.commit()


@api.route('/teacher/availability/delete/<int:availability_id>', methods=['POST'])
@login_required
def delete_availability(availability_id):
    availability = Availability.query.get_or_404(availability_id)
    
    if availability.teacher_id != current_user.id:
        flash('Unauthorized action.')
        return redirect(url_for('api.set_availability'))
    
    db.session.delete(availability)
    db.session.commit()
    
    flash('Availability deleted successfully!')
    return redirect(url_for('api.set_availability'))


def convert_time(dt, from_timezone, to_timezone):
    """Convert the datetime object 'dt' from 'from_timezone' to 'to_timezone'."""
    from_tz = pytz.timezone(from_timezone)
    to_tz = pytz.timezone(to_timezone)
    
    if dt.tzinfo is None:
        dt = from_tz.localize(dt)

    converted_time = dt.astimezone(to_tz)
    return converted_time


@api.route('/student/book/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(teacher_id):
    if current_user.role != 'student':
        return redirect(url_for('api.home'))

    form = AppointmentForm()
    teacher = User.query.get(teacher_id)

    student_timezone = current_user.time_zone  
    if not student_timezone:
        flash('Student timezone is not set. Please update your profile.')
        return redirect(url_for('api.edit_profile'))

    slots = generate_available_slots(teacher, student_timezone)
    form.slot_time.choices = [(str(slot), slot.strftime('%Y-%m-%d %H:%M')) for slot in slots]

    if form.validate_on_submit():
        selected_slot_time = parser.parse(form.slot_time.data)
        teacher_timezone = teacher.time_zone

        slot_time = convert_time(selected_slot_time, teacher_timezone, student_timezone)

        if slot_time.tzinfo is None:
            slot_time = slot_time.astimezone(pytz.timezone(student_timezone))

        new_appointment = Appointment(
            student_id=current_user.id,
            teacher_id=teacher_id,
            slot_time=slot_time,
            title=form.title.data,
            description=form.description.data,
            material_url=form.material_url.data,
            google_meet_link=form.google_meet_link.data,
            status=Appointment.PENDING
        )

        confirmed_slots = Appointment.query.filter_by(teacher_id=teacher_id, status=Appointment.CONFIRMED).all()
        if is_time_slot_available(slot_time, slot_time + timedelta(hours=1), confirmed_slots, student_timezone):
            db.session.add(new_appointment)
            db.session.commit()

            socketio.emit('appointment_request', {
                'teacher_id': teacher_id,
                'student_name': current_user.username,
                'appointment_title': form.title.data,
                'appointment_time': slot_time.strftime('%Y-%m-%d %H:%M'),
                'student_timezone': student_timezone
            }, namespace='/notifications')

            flash('Appointment request sent!')
            return redirect(url_for('api.home'))
        else:
            flash('Selected time slot is already booked. Please choose another time.')

    return render_template('book_appointment.html', form=form, teacher=teacher, slots=slots)


def generate_available_slots(teacher, student_timezone, session_duration=60):
    """Generate available time slots for the teacher, excluding past slots."""
    slots = []
    availabilities = Availability.query.filter_by(teacher_id=teacher.id).all()

    confirmed_slots = Appointment.query.filter_by(teacher_id=teacher.id, status=Appointment.CONFIRMED).all()
    confirmed_slot_times = [convert_time(appointment.slot_time, teacher.time_zone, student_timezone) for appointment in confirmed_slots]

    teacher_timezone = teacher.time_zone
    now_in_teacher_tz = datetime.now(pytz.timezone(teacher_timezone))

    for availability in availabilities:
        start = datetime.combine(datetime.today(), availability.start_time)
        end = datetime.combine(datetime.today(), availability.end_time)
        
        start = pytz.timezone(teacher_timezone).localize(start)
        end = pytz.timezone(teacher_timezone).localize(end)

        if start < now_in_teacher_tz:
            continue

        while start < end:
            if not any(start == confirmed_time for confirmed_time in confirmed_slot_times):
                converted_slot = convert_time(start, teacher_timezone, student_timezone)
                slots.append(converted_slot)
            start += timedelta(minutes=session_duration)

    return slots



def is_time_slot_available(new_slot_start, new_slot_end, confirmed_slots, student_timezone):
    """Check if a new slot overlaps with confirmed slots."""
    student_timezone = pytz.timezone(student_timezone)

    for confirmed_slot in confirmed_slots:
        confirmed_start = confirmed_slot.slot_time
        confirmed_end = confirmed_slot.slot_time + timedelta(hours=1)

        if confirmed_start.tzinfo is None:
            confirmed_start = pytz.utc.localize(confirmed_start)
        if confirmed_end.tzinfo is None:
            confirmed_end = pytz.utc.localize(confirmed_end)

        confirmed_start = confirmed_start.astimezone(student_timezone)
        confirmed_end = confirmed_end.astimezone(student_timezone)

        if new_slot_start < confirmed_end and new_slot_end > confirmed_start:
            return False
    return True


def get_next_appointment():
    next_appointment = Appointment.query.filter(
        or_(Appointment.student_id == current_user.id, Appointment.teacher_id == current_user.id),
        Appointment.status == Appointment.CONFIRMED
    ).order_by(Appointment.slot_time).first()
    
    return next_appointment


def get_suggested_teachers(current_user_subject):

    if not current_user_subject:
        return ([], "We cannot find suitable matches. Consider adding new subjects to your profile.")

    user_subjects = [subject.strip() for subject in current_user_subject.split(',')]

    suggested_teachers = User.query.filter(
        User.role == 'teacher'
    ).filter(
        or_(*[User.subject.ilike(f"%{subject}%") for subject in user_subjects])
    ).join(Availability).filter(Availability.teacher_id == User.id).distinct().limit(5).all()


    if not suggested_teachers:
        return ([], "We cannot find suitable matches. Consider adding new subjects to your profile.")

    return (suggested_teachers, None)


@api.route('/calendar', methods=['GET'])
@login_required
def calendar():
    appointments = Appointment.query.filter(
        or_(Appointment.student_id == current_user.id, Appointment.teacher_id == current_user.id),
        Appointment.status == Appointment.CONFIRMED
    ).all()

    events = [{
        'id': appointment.id,
        'title': f"{appointment.title} (with {appointment.teacher.username if current_user.role == 'student' else appointment.student.username})",
        'start': appointment.slot_time.isoformat(),
        'end': (appointment.slot_time + timedelta(hours=1)).isoformat(),
        'description': appointment.description,
        'material_url': appointment.material_url,
        'google_meet_link': appointment.google_meet_link,
        'status': appointment.status,
        'with': appointment.teacher.username if current_user.role == 'student' else appointment.student.username,
    } for appointment in appointments]

    return render_template('calendar.html', events=events)


@socketio.on('connect', namespace='/notifications')
def connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect', namespace='/notifications')
def disconnect():
    print(f'Client disconnected: {request.sid}')
