from datetime import date
from flask import Blueprint,render_template,request,redirect,url_for
from models import *
from flask import session
from extension import db
from booking_rules import (
    booking_window_open,
    exam_phase,
    display_status,
    mark_finished_bookings,
    slot_is_full,
    refresh_slot_closed,
    active_counts,
)


def _slot_visible(exam, today=None):
    today = today or date.today()
    if booking_window_open(exam, today):
        return True
    return bool(exam and exam.is_slot_creation_open)


def cancellation_open(exam, today=None):
    today = today or date.today()
    if not exam:
        return False
    if exam.booking_close_date:
        return today <= exam.booking_close_date
    return bool(exam.is_booking_open)


def _matches_exam(term, exam):
    if not term:
        return True
    if term.isdigit():
        return str(exam.id) == term
    return term.lower() in (exam.exam_name or '').lower()

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route('/user_dashboard',methods=['GET'])
def user_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    profile = User_profile.query.filter_by(user_id=user_id).first()
    exams = Exam.query.order_by(Exam.exam_date).all()
    courses = {course.id: course for course in Course.query.all()}
    bookings = SlotBooking.query.filter_by(student_id=user_id).all()
    exam_map = {exam.id: exam for exam in exams}
    slot_map = {slot.id: slot for slot in ExamSlot.query.all()}
    mark_finished_bookings(bookings, exam_map, slot_map)
    counts = active_counts()
    booked_exam_ids = {booking.exam_id for booking in bookings if booking.status == 'Booked'}
    open_slots = [
        slot for slot in ExamSlot.query.order_by(ExamSlot.slot_date).all()
        if not slot_is_full(slot, counts)
        and slot.exam_id not in booked_exam_ids
        and _slot_visible(exam_map.get(slot.exam_id))
    ]
    mark_summary = {}
    if bookings:
        exam_ids = {booking.exam_id for booking in bookings}
        questions = quetionBank.query.filter(quetionBank.exam_id.in_(exam_ids)).all()
        possible = {}
        for question in questions:
            possible[question.exam_id] = possible.get(question.exam_id, 0) + question.marks
        marks = StudentMark.query.filter(
            StudentMark.student_id == user_id,
            StudentMark.exam_id.in_(exam_ids)
        ).all()
        awarded = {}
        for mark in marks:
            awarded[mark.exam_id] = awarded.get(mark.exam_id, 0) + mark.marks_awarded
        for booking in bookings:
            mark_summary[booking.id] = {
                'awarded': awarded.get(booking.exam_id) if exam_map[booking.exam_id].results_published else None,
                'possible': possible.get(booking.exam_id, 0),
                'published': bool(exam_map[booking.exam_id].results_published)
            }
    cancel_open = {
        booking.id: booking.status == 'Booked' and cancellation_open(exam_map.get(booking.exam_id), date.today())
        for booking in bookings
    }
    statuses = {booking.id: display_status(booking) for booking in bookings}
    return render_template(
        'user/user_dashboard.html',
        user=user,
        profile=profile,
        exams=exams,
        courses=courses,
        open_slots=open_slots,
        bookings=bookings,
        exam_map=exam_map,
        slot_map=slot_map,
        mark_summary=mark_summary,
        cancel_open=cancel_open,
        statuses=statuses,
        phases={exam.id: exam_phase(exam) for exam in exams},
        can_book={exam.id: booking_window_open(exam) for exam in exams},
        today=date.today()
    )


def _student_records(user_id):
    bookings = SlotBooking.query.filter_by(student_id=user_id).all()
    exam_ids = {booking.exam_id for booking in bookings}
    exams = {exam.id: exam for exam in (Exam.query.filter(Exam.id.in_(exam_ids)).all() if exam_ids else [])}
    slots = {slot.id: slot for slot in ExamSlot.query.filter(ExamSlot.id.in_({booking.slot_id for booking in bookings})).all()} if bookings else {}
    return bookings, exams, slots


@user_blueprint.route('/exams', methods=['GET'])
def exams():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    term = (request.args.get('q') or '').strip()
    course_filter = (request.args.get('course') or '').strip()
    booking_filter = (request.args.get('booking') or 'all').strip()
    when_filter = (request.args.get('when') or 'all').strip()
    today = date.today()
    courses = Course.query.order_by(Course.coures_name).all()
    course_map = {course.id: course for course in courses}
    user_id = session.get('user_id')
    student_bookings = SlotBooking.query.filter_by(student_id=user_id, status='Booked').all()
    booked_exam_ids = {booking.exam_id for booking in student_bookings}
    counts = active_counts()
    exam_lookup = {exam.id: exam for exam in Exam.query.all()}
    slots_by_exam = {}
    for slot in ExamSlot.query.order_by(ExamSlot.slot_date).all():
        if (
            _slot_visible(exam_lookup.get(slot.exam_id))
            and not slot_is_full(slot, counts)
            and slot.exam_id not in booked_exam_ids
        ):
            slots_by_exam.setdefault(slot.exam_id, []).append(slot)
    visible = []
    for exam in Exam.query.order_by(Exam.exam_date).all():
        if not _matches_exam(term, exam):
            continue
        if course_filter and str(exam.coures_id) != course_filter:
            continue
        if booking_filter == 'open' and not exam.is_booking_open:
            continue
        if booking_filter == 'closed' and exam.is_booking_open:
            continue
        if when_filter == 'upcoming' and exam.exam_date < today:
            continue
        if when_filter == 'past' and exam.exam_date >= today:
            continue
        visible.append(exam)
    return render_template(
        'user/exams.html',
        exams=visible,
        courses=courses,
        course_map=course_map,
        slots_by_exam=slots_by_exam,
        booked_exam_ids=booked_exam_ids,
        q=term,
        course_filter=course_filter,
        booking_filter=booking_filter,
        when_filter=when_filter,
        phases={exam.id: exam_phase(exam) for exam in visible},
        can_book={exam.id: booking_window_open(exam) for exam in visible},
        today=today
    )


@user_blueprint.route('/bookings', methods=['GET'])
def bookings():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    user_id = session.get('user_id')
    rows, exams, slots = _student_records(user_id)
    today = date.today()
    mark_finished_bookings(rows, exams, slots, today)
    details = []
    for booking in rows:
        exam = exams.get(booking.exam_id)
        slot = slots.get(booking.slot_id)
        details.append({
            'booking': booking,
            'exam': exam,
            'slot': slot,
            'status': display_status(booking),
            'can_cancel': booking.status == 'Booked' and cancellation_open(exam, today),
            'published': bool(exam and exam.results_published)
        })
    return render_template('user/bookings.html', details=details)


@user_blueprint.route('/history', methods=['GET'])
def history():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    user_id = session.get('user_id')
    rows, exams, slots = _student_records(user_id)
    today = date.today()
    mark_finished_bookings(rows, exams, slots, today)
    past = []
    for booking in rows:
        exam = exams.get(booking.exam_id)
        slot = slots.get(booking.slot_id)
        if booking.status in ('Completed', 'Cancelled'):
            past.append({
                'booking': booking,
                'exam': exam,
                'slot': slot,
                'status': display_status(booking),
                'published': bool(exam and exam.results_published)
            })
    past.sort(key=lambda item: item['exam'].exam_date if item['exam'] else date.min, reverse=True)
    return render_template('user/history.html', past=past)


@user_blueprint.route('/my_marks', methods=['GET'])
def my_marks():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    user_id = session.get('user_id')
    bookings = SlotBooking.query.filter_by(student_id=user_id).all()
    marks = StudentMark.query.filter_by(student_id=user_id).all()
    exam_ids = {booking.exam_id for booking in bookings}
    exam_ids.update(mark.exam_id for mark in marks)
    exams = Exam.query.filter(Exam.id.in_(exam_ids)).order_by(Exam.exam_date).all() if exam_ids else []
    published_ids = {exam.id for exam in exams if exam.results_published}
    questions = quetionBank.query.filter(quetionBank.exam_id.in_(published_ids)).all() if published_ids else []
    questions_by_exam = {}
    for question in questions:
        questions_by_exam.setdefault(question.exam_id, []).append(question)
    marks_by_question = {
        mark.question_id: mark.marks_awarded
        for mark in marks
        if mark.exam_id in published_ids
    }
    remarks = {
        item.exam_id: item.remark
        for item in ExamRemark.query.filter_by(student_id=user_id).all()
        if item.exam_id in published_ids
    }
    return render_template(
        'user/my_marks.html',
        exams=exams,
        questions_by_exam=questions_by_exam,
        marks_by_question=marks_by_question,
        remarks=remarks
    )


@user_blueprint.route('/book_slot/<int:slot_id>', methods=['GET'])
def book_slot(slot_id):
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    student_id = session.get('user_id')
    slot = ExamSlot.query.get(slot_id)
    if not slot:
        return redirect(url_for('user.user_dashboard'))
    exam = Exam.query.get(slot.exam_id)
    already_booked_exam = SlotBooking.query.filter_by(
        student_id=student_id, exam_id=slot.exam_id, status='Booked'
    ).first()
    if booking_window_open(exam) and not slot_is_full(slot) and not already_booked_exam:
        booking = SlotBooking(
            slot_id=slot.id,
            exam_id=slot.exam_id,
            student_id=student_id,
            status='Booked'
        )
        db.session.add(booking)
        db.session.flush()
        refresh_slot_closed(slot)
        db.session.commit()
    return redirect(url_for('user.user_dashboard'))


@user_blueprint.route('/cancel_booking/<int:booking_id>', methods=['GET'])
def cancel_booking(booking_id):
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    booking = SlotBooking.query.get(booking_id)
    if booking and booking.student_id == session.get('user_id'):
        exam = Exam.query.get(booking.exam_id)
        if booking.status == 'Booked' and cancellation_open(exam):
            booking.status = 'Cancelled'
            slot = ExamSlot.query.get(booking.slot_id)
            if slot:
                refresh_slot_closed(slot)
            db.session.commit()
    return redirect(url_for('user.bookings'))


@user_blueprint.route('/create_profile',methods=['POST','GET'])
def create_profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    profile = User_profile.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']
        past_experience = request.form['past_experience']
        if profile:
            profile.address = address
            profile.phone = phone
            profile.past_experience = past_experience
        else:
            profile = User_profile(address=address,phone=phone,past_experience=past_experience,user_id=user_id)
            db.session.add(profile)
        db.session.commit()
        return redirect(url_for('user.user_dashboard'))
    return render_template('user/create_profile.html', profile=profile, user=user)


@user_blueprint.route('/edit_profile',methods=['POST','GET'])
def edit_profile():
    user_id = session.get('user_id')
    profile = User_profile.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        address = request.form['address']
        phone = request.form['phone']
        past_experience = request.form['past_experience']
        profile.address = address
        profile.phone = phone
        profile.past_experience = past_experience
        db.session.commit()
        return redirect(url_for('user.user_dashboard'))
    return render_template('user/edit_profile.html', profile=profile)
