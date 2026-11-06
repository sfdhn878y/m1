from datetime import datetime, date
from flask import Blueprint,render_template,request,redirect,url_for
from models import *
from flask import session
from extension import db

examior_blueprint = Blueprint("examior", __name__)


@examior_blueprint.before_request
def require_approved_examiner():
    if session.get('role') != 'examinor':
        return redirect(url_for('index'))
    user = User.query.get(session.get('user_id'))
    if not user or not user.is_verified:
        session.pop('user_id', None)
        session.pop('role', None)
        return redirect(url_for('auth.login', pending=1))


def _booking_started(exam):
    if not exam:
        return True
    if exam.is_booking_open:
        return True
    if exam.booking_open_date and date.today() >= exam.booking_open_date:
        return True
    return False


def _slot_creation_open(exam):
    if not exam.slot_creation_start_date or not exam.slot_creation_end_date:
        return False
    today = date.today()
    return exam.slot_creation_start_date <= today <= exam.slot_creation_end_date


def _slot_change_allowed(exam, slot):
    if _booking_started(exam):
        return False
    if SlotBooking.query.filter_by(slot_id=slot.id).first():
        return False
    return True


def _examiner_bookings(examinor_id):
    assigned_exams = Exam.query.filter_by(examinor_id=examinor_id).all()
    exam_ids = [exam.id for exam in assigned_exams]
    bookings = SlotBooking.query.filter(SlotBooking.exam_id.in_(exam_ids)).all() if exam_ids else []
    exam_map = {exam.id: exam for exam in assigned_exams}
    slot_map = {
        slot.id: slot for slot in ExamSlot.query.filter(ExamSlot.id.in_([booking.slot_id for booking in bookings])).all()
    } if bookings else {}
    student_map = {
        student.id: student for student in User.query.filter(User.id.in_([booking.student_id for booking in bookings])).all()
    } if bookings else {}
    return assigned_exams, bookings, exam_map, slot_map, student_map


def _mark_summary(bookings):
    summary = {}
    if not bookings:
        return summary
    exam_ids = {booking.exam_id for booking in bookings}
    student_ids = {booking.student_id for booking in bookings}
    questions = quetionBank.query.filter(quetionBank.exam_id.in_(exam_ids)).all()
    possible = {}
    for question in questions:
        possible[question.exam_id] = possible.get(question.exam_id, 0) + question.marks
    marks = StudentMark.query.filter(
        StudentMark.exam_id.in_(exam_ids),
        StudentMark.student_id.in_(student_ids)
    ).all()
    awarded = {}
    for mark in marks:
        key = (mark.exam_id, mark.student_id)
        awarded[key] = awarded.get(key, 0) + mark.marks_awarded
    for booking in bookings:
        key = (booking.exam_id, booking.student_id)
        summary[booking.id] = {
            'awarded': awarded.get(key),
            'possible': possible.get(booking.exam_id, 0)
        }
    return summary


@examior_blueprint.route('/examior_dashboard',methods=['POST','GET'])
def examior_dashboard():
    user = User.query.get(session.get('user_id'))
    profile = Staff_Profile.query.filter_by(user_id=session.get('user_id')).first()
    assigned_exams, bookings, exam_map, slot_map, student_map = _examiner_bookings(session.get('user_id'))
    return render_template(
        'examior/examior_dashboard.html',
        user=user,
        profile=profile,
        assigned_exams=assigned_exams,
        bookings=bookings,
        exam_map=exam_map,
        slot_map=slot_map,
        student_map=student_map,
        mark_summary=_mark_summary(bookings)
    )


@examior_blueprint.route('/see_bookings', methods=['GET'])
def see_bookings():
    if session.get('role') != 'examinor':
        return redirect(url_for('index'))
    assigned_exams, bookings, exam_map, slot_map, student_map = _examiner_bookings(session.get('user_id'))
    return render_template(
        'examior/see_bookings.html',
        bookings=bookings,
        exam_map=exam_map,
        slot_map=slot_map,
        student_map=student_map,
        mark_summary=_mark_summary(bookings)
    )


@examior_blueprint.route('/view_booking/<int:booking_id>', methods=['GET'])
def view_booking(booking_id):
    if session.get('role') != 'examinor':
        return redirect(url_for('index'))
    booking = SlotBooking.query.get(booking_id)
    exam = Exam.query.get(booking.exam_id) if booking else None
    if not booking or not exam or exam.examinor_id != session.get('user_id'):
        return redirect(url_for('examior.see_bookings'))
    student = User.query.get(booking.student_id)
    profile = User_profile.query.filter_by(user_id=student.id).first()
    slot = ExamSlot.query.get(booking.slot_id)
    remark = ExamRemark.query.filter_by(exam_id=exam.id, student_id=student.id).first()
    return render_template(
        'examior/view_booking.html',
        booking=booking,
        exam=exam,
        student=student,
        profile=profile,
        slot=slot,
        remark=remark
    )


@examior_blueprint.route('/give_marks/<int:booking_id>', methods=['GET', 'POST'])
def give_marks(booking_id):
    if session.get('role') != 'examinor':
        return redirect(url_for('index'))
    booking = SlotBooking.query.get(booking_id)
    exam = Exam.query.get(booking.exam_id) if booking else None
    if not booking or not exam or exam.examinor_id != session.get('user_id'):
        return redirect(url_for('examior.see_bookings'))
    student = User.query.get(booking.student_id)
    questions = quetionBank.query.filter_by(exam_id=exam.id).all()
    saved = {
        mark.question_id: mark
        for mark in StudentMark.query.filter_by(exam_id=exam.id, student_id=student.id).all()
    }
    remark = ExamRemark.query.filter_by(exam_id=exam.id, student_id=student.id).first()
    error = None
    if request.method == 'POST':
        awarded = {}
        for question in questions:
            raw = (request.form.get(f'marks_{question.id}') or '').strip()
            try:
                value = int(raw)
            except ValueError:
                error = 'Enter a whole number for every question.'
                break
            if value < 0 or value > question.marks:
                error = f'Marks for "{question.question}" must be from 0 to {question.marks}.'
                break
            awarded[question.id] = value
        if not error and not questions:
            error = 'This exam has no rubric yet.'
        if not error:
            for question in questions:
                row = saved.get(question.id)
                if row:
                    row.marks_awarded = awarded[question.id]
                    row.given_by = session.get('user_id')
                else:
                    db.session.add(StudentMark(
                        exam_id=exam.id,
                        student_id=student.id,
                        question_id=question.id,
                        marks_awarded=awarded[question.id],
                        given_by=session.get('user_id')
                    ))
            remark_text = (request.form.get('remark') or '').strip()
            if remark:
                remark.remark = remark_text
                remark.given_by = session.get('user_id')
            elif remark_text:
                db.session.add(ExamRemark(
                    exam_id=exam.id,
                    student_id=student.id,
                    remark=remark_text,
                    given_by=session.get('user_id')
                ))
            db.session.commit()
            return redirect(url_for('examior.see_bookings'))
    return render_template(
        'examior/give_marks.html',
        exam=exam,
        student=student,
        questions=questions,
        saved=saved,
        remark=remark,
        error=error
    )


@examior_blueprint.route('/create_profile',methods=['POST','GET'])
def create_profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    profile = Staff_Profile.query.filter_by(user_id=user_id).first()
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
            profile = Staff_Profile(address=address,phone=phone,past_experience=past_experience,user_id=user_id)
            db.session.add(profile)
        db.session.commit()
        return redirect(url_for('examior.examior_dashboard'))
    return render_template('examior/create_profile.html', profile=profile, user=user)



@examior_blueprint.route('/edit_profile',methods=['POST','GET'])
def edit_profile():
    user_id = session.get('user_id')
   
    profile = Staff_Profile.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
      
        
        address = request.form['address']
        phone = request.form['phone']
        past_experience = request.form['past_experience']
        profile.address = address
        profile.phone = phone
        profile.past_experience = past_experience
        db.session.commit()
        return redirect(url_for('examior.examior_dashboard'))
    return render_template('examior/edit_profile.html', profile=profile)




@examior_blueprint.route('/see_assigned_exams',methods=['POST','GET'])
def see_assigned_exams():
    examior_id = session.get('user_id')
    assigned_exams = Exam.query.filter_by(examinor_id=examior_id).all()
    courses = {course.id: course for course in Course.query.all()}
    return render_template('examior/see_assigned_exams.html', assigned_exams=assigned_exams, courses=courses)


@examior_blueprint.route('/publish_results/<int:exam_id>', methods=['GET', 'POST'])
def publish_results(exam_id):
    exam = Exam.query.get(exam_id)
    if not exam or exam.examinor_id != session.get('user_id'):
        return redirect(url_for('examior.see_assigned_exams'))
    exam.results_published = True
    db.session.commit()
    return redirect(url_for('examior.see_assigned_exams'))


def _parse_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


@examior_blueprint.route('/provide_slot/<int:exam_id>', methods=['POST', 'GET'])
def provide_slot(exam_id):
    examior_id = session.get('user_id')
    exam = Exam.query.get(exam_id)
    if not exam or exam.examinor_id != examior_id:
        return redirect(url_for('examior.see_assigned_exams'))

    error = None
    if request.method == 'POST':
        slot_date = _parse_date(request.form.get('slot_date'))
        if not exam.slot_creation_start_date or not exam.slot_creation_end_date:
            error = 'The admin has not set the slot creation dates for this exam yet.'
        elif not slot_date:
            error = 'Select a valid slot date.'
        elif not _slot_creation_open(exam):
            error = (
                'You can create slots only from '
                f'{exam.slot_creation_start_date} to {exam.slot_creation_end_date}.'
            )
        elif slot_date < exam.slot_creation_start_date or slot_date > exam.slot_creation_end_date:
            error = (
                'You can create a slot only between '
                f'{exam.slot_creation_start_date} and '
                f'{exam.slot_creation_end_date}, the dates set by the admin.'
            )
        elif ExamSlot.query.filter_by(exam_id=exam.id, slot_date=slot_date).first():
            error = 'A slot already exists on this date.'
        else:
            slot = ExamSlot(
                exam_id=exam.id,
                slot_date=slot_date,
                created_by=examior_id
            )
            db.session.add(slot)
            db.session.commit()
            return redirect(url_for('examior.provide_slot', exam_id=exam.id))

    slots = ExamSlot.query.filter_by(exam_id=exam.id).order_by(ExamSlot.slot_date).all()
    slot_ids = [slot.id for slot in slots]
    bookings = SlotBooking.query.filter(SlotBooking.slot_id.in_(slot_ids)).all() if slot_ids else []
    booking_by_slot = {booking.slot_id: booking for booking in bookings}
    student_map = {
        student.id: student for student in User.query.filter(User.id.in_([booking.student_id for booking in bookings])).all()
    } if bookings else {}
    return render_template(
        'examior/provide_slot.html',
        exam=exam,
        slots=slots,
        error=error,
        booking_by_slot=booking_by_slot,
        student_map=student_map,
        booking_started=_booking_started(exam),
        creation_open=_slot_creation_open(exam)
    )


@examior_blueprint.route('/edit_slot/<int:slot_id>', methods=['GET', 'POST'])
def edit_slot(slot_id):
    slot = ExamSlot.query.get(slot_id)
    exam = Exam.query.get(slot.exam_id) if slot else None
    if not slot or not exam or exam.examinor_id != session.get('user_id'):
        return redirect(url_for('examior.see_assigned_exams'))
    if not _slot_change_allowed(exam, slot):
        return redirect(url_for('examior.provide_slot', exam_id=exam.id))
    error = None
    if request.method == 'POST':
        slot_date = _parse_date(request.form.get('slot_date'))
        if not slot_date:
            error = 'Select a valid slot date.'
        elif slot_date < exam.slot_creation_start_date or slot_date > exam.slot_creation_end_date:
            error = (
                'The slot date must stay between '
                f'{exam.slot_creation_start_date} and {exam.slot_creation_end_date}.'
            )
        else:
            taken = ExamSlot.query.filter_by(exam_id=exam.id, slot_date=slot_date).first()
            if taken and taken.id != slot.id:
                error = 'A slot already exists on this date.'
            else:
                slot.slot_date = slot_date
                db.session.commit()
                return redirect(url_for('examior.provide_slot', exam_id=exam.id))
    return render_template('examior/edit_slot.html', exam=exam, slot=slot, error=error)


@examior_blueprint.route('/delete_slot/<int:slot_id>', methods=['POST', 'GET'])
def delete_slot(slot_id):
    slot = ExamSlot.query.get(slot_id)
    exam = Exam.query.get(slot.exam_id) if slot else None
    if not slot or not exam or slot.created_by != session.get('user_id'):
        return redirect(url_for('examior.see_assigned_exams'))
    if not _slot_change_allowed(exam, slot):
        return redirect(url_for('examior.provide_slot', exam_id=exam.id))
    db.session.delete(slot)
    db.session.commit()
    return redirect(url_for('examior.provide_slot', exam_id=exam.id))