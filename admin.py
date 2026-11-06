

from models import *
from flask import Blueprint
admin_blueprint = Blueprint('admin',__name__)




@admin_blueprint.route('/admin_dashboard',methods=['POST','GET'])
def admin_dashboard():
    course_count = Course.query.count()
    exam_count = Exam.query.count()
    student_count = User.query.filter_by(role='student').count()
    examinor_count = User.query.filter_by(role='examinor').count()
    return render_template(
        '/admin/admin_dashboard.html',
        course_count=course_count,
        exam_count=exam_count,
        student_count=student_count,
        examinor_count=examinor_count
    )



@admin_blueprint.route('/manage_courses',methods=['POST','GET'])
def manage_courses():
    courses = Course.query.all()
    print(courses)
  
    return render_template('/admin/manage_courses.html',courses=courses)



def _query_text():
    return (request.args.get('q') or '').strip()


def _matches_name_or_id(term, record_id, name):
    if not term:
        return True
    if term.isdigit() and int(term) == record_id:
        return True
    return term.lower() in (name or '').lower()


def _booking_matches(term, booking, exam, student):
    if not term:
        return True
    if _matches_name_or_id(term, booking.id, ''):
        return True
    if student and _matches_name_or_id(term, student.id, student.name):
        return True
    if exam and _matches_name_or_id(term, exam.id, exam.exam_name):
        return True
    return False


@admin_blueprint.route('/manage_exams',methods=['POST','GET'])
def manage_exams():
    q = _query_text()
    exams = [exam for exam in Exam.query.all() if _matches_name_or_id(q, exam.id, exam.exam_name)]
    return render_template('/admin/manage_exams.html', exams=exams, q=q)


@admin_blueprint.route('/edit_course/<int:id>',methods=['POST','GET'])
def edit_course(id):
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_description = request.form['course_description']
        course_duration = request.form['course_duration']
        course = Course.query.get(id)
        course.coures_name = course_name
        course.coures_description = course_description
        course.course_duration = course_duration
        db.session.commit()
        return redirect(url_for('admin.admin_dashboard'))
    course = Course.query.get(id)
    return render_template('/admin/edit_course.html',course=course)




@admin_blueprint.route('/create_course',methods=['POST','GET'])
def create_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_description = request.form['course_description']
        course_duration = request.form['course_duration']
        course = Course(coures_name=course_name,coures_description=course_description,course_duration=course_duration)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('/admin/create_course.html')

@admin_blueprint.route('/delete/<int:id>',methods=['POST','GET'])
def delete(id):
    exams = Exam.query.filter_by(coures_id=id).all()
    for exam in exams:
        quetionBank.query.filter_by(exam_id=exam.id).delete()
        StudentMark.query.filter_by(exam_id=exam.id).delete()
        ExamRemark.query.filter_by(exam_id=exam.id).delete()
        SlotBooking.query.filter_by(exam_id=exam.id).delete()
        ExamSlot.query.filter_by(exam_id=exam.id).delete()
        db.session.delete(exam)
    course = Course.query.get(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin.manage_courses'))

from datetime import datetime
from flask import request, render_template, redirect, url_for

@admin_blueprint.route('/create_exam', methods=['POST', 'GET'])
def create_exam():

    examinors = User.query.filter_by(role='examinor').all()
    courses = Course.query.all()

    if request.method == 'POST':

        exam_name = request.form['exam_name']
        exam_description = request.form['exam_description']

        exam_date = datetime.strptime(
            request.form['exam_date'], '%Y-%m-%d'
        ).date()

        exam_time = datetime.strptime(
            request.form['exam_time'], '%H:%M'
        ).time()

        slot_start_time = datetime.strptime(
            request.form['slot_start_time'], '%H:%M'
        ).time()

        slot_end_time = datetime.strptime(
            request.form['slot_end_time'], '%H:%M'
        ).time()

        booking_open_date = datetime.strptime(
            request.form['booking_open_date'], '%Y-%m-%d'
        ).date()
        booking_close_date = datetime.strptime(
            request.form['booking_close_date'], '%Y-%m-%d'
        ).date()
        if booking_close_date < booking_open_date:
            return render_template(
                '/admin/create_exam.html',
                examinors=examinors,
                courses=courses,
                error='Booking close date must be on or after the date booking opens.'
            )

        slot_creation_start_date = datetime.strptime(
            request.form['slot_creation_start_date'], '%Y-%m-%d'
        ).date()
        slot_creation_end_date = datetime.strptime(
            request.form['slot_creation_end_date'], '%Y-%m-%d'
        ).date()
        if slot_creation_end_date < slot_creation_start_date:
            return render_template(
                '/admin/create_exam.html',
                examinors=examinors,
                courses=courses,
                error='Slot creation end date must be on or after the start date.'
            )

        exam_duration = int(request.form['exam_duration'])
        examinor_id = int(request.form['examinor_id'])
        user = User.query.get(examinor_id)
        examinor_name = user.name
        course_id = int(request.form['course_id'])

        exam = Exam(
            exam_name=exam_name,
            exam_description=exam_description,
            exam_date=exam_date,
            exam_time=exam_time,
            exam_duration=exam_duration,
            slot_start_time=slot_start_time,
            slot_end_time=slot_end_time,
            slot_creation_start_date=slot_creation_start_date,
            slot_creation_end_date=slot_creation_end_date,
            booking_start_time=datetime.strptime('00:00', '%H:%M').time(),
            booking_end_time=datetime.strptime('00:00', '%H:%M').time(),
            booking_open_date=booking_open_date,
            booking_close_date=booking_close_date,
            examinor_id=examinor_id,
            coures_id=course_id,
            examinor_name=examinor_name
        )

        db.session.add(exam)
        db.session.commit()

        return redirect(url_for('admin.admin_dashboard'))

    return render_template(
        '/admin/create_exam.html',
        examinors=examinors,
        courses=courses
    )

@admin_blueprint.route('/create_rubric/<int:id>',methods=['POST','GET'])
def create_rubric(id):
    if request.method == 'POST':
        question = request.form['question']
        marks = request.form['marks']
        exam_id = request.form['exam_id']
        rubric = quetionBank(question=question,marks=marks,exam_id=exam_id)
        db.session.add(rubric)
        db.session.commit()
        return redirect(url_for('admin.admin_dashboard'))
 
    return render_template('/admin/create_rubic.html',id=id)



@admin_blueprint.route('/manage_rubric/<int:id>',methods=['POST','GET'])
def manage_rubric(id):
    questions = quetionBank.query.filter_by(exam_id=id).all()
    return render_template('/admin/manage_rubric.html',questions=questions,exam_id=id)


@admin_blueprint.route('/edit_rubric/<int:id>', methods=['POST', 'GET'])
def edit_rubric(id):
    rubric = quetionBank.query.get(id)
    if request.method == 'POST':
        rubric.question = request.form['question']
        rubric.marks = request.form['marks']
        db.session.commit()
        return redirect(url_for('admin.manage_rubric', id=rubric.exam_id))
    return render_template('/admin/edit_rubric.html', rubric=rubric)


@admin_blueprint.route('/delete_rubric/<int:id>', methods=['POST', 'GET'])
def delete_rubric(id):
    rubric = quetionBank.query.get(id)
    exam_id = rubric.exam_id
    StudentMark.query.filter_by(question_id=rubric.id).delete()
    db.session.delete(rubric)
    db.session.commit()
    return redirect(url_for('admin.manage_rubric', id=exam_id))


def _edit_exam_context(exam):
    examinors = User.query.filter_by(role='examinor').all()
    courses = Course.query.all()
    booked_rows = db.session.query(Exam.id, Exam.examinor_id).join(
        SlotBooking, SlotBooking.exam_id == Exam.id
    ).all()
    this_exam_booked = any(row.id == exam.id for row in booked_rows)
    busy_examiner_ids = {row.examinor_id for row in booked_rows if row.id != exam.id}
    return examinors, courses, busy_examiner_ids, this_exam_booked


@admin_blueprint.route('/edit_exam/<int:id>', methods=['POST', 'GET'])
def edit_exam(id):
    exam = Exam.query.get(id)
    examinors, courses, busy_examiner_ids, this_exam_booked = _edit_exam_context(exam)

    def show(error=None):
        return render_template(
            '/admin/edit_exam.html',
            exam=exam,
            examinors=examinors,
            courses=courses,
            error=error,
            busy_examiner_ids=busy_examiner_ids,
            this_exam_booked=this_exam_booked
        )

    if request.method == 'POST':
        examinor_id = int(request.form['examinor_id'])
        if examinor_id != exam.examinor_id:
            if this_exam_booked:
                return show('Students have booked slots for this exam. Delete this examination before changing the examiner.')
            if examinor_id in busy_examiner_ids:
                return show('That examiner is not free. They have booked slots on another examination. Delete that examination first.')
        exam.exam_name = request.form['exam_name']
        exam.exam_description = request.form['exam_description']
        exam.exam_date = datetime.strptime(request.form['exam_date'], '%Y-%m-%d').date()
        exam.exam_time = datetime.strptime(request.form['exam_time'], '%H:%M').time()
        exam.slot_start_time = datetime.strptime(request.form['slot_start_time'], '%H:%M').time()
        exam.slot_end_time = datetime.strptime(request.form['slot_end_time'], '%H:%M').time()
        slot_creation_start_date = datetime.strptime(request.form['slot_creation_start_date'], '%Y-%m-%d').date()
        slot_creation_end_date = datetime.strptime(request.form['slot_creation_end_date'], '%Y-%m-%d').date()
        if slot_creation_end_date < slot_creation_start_date:
            return show('Slot creation end date must be on or after the start date.')
        exam.slot_creation_start_date = slot_creation_start_date
        exam.slot_creation_end_date = slot_creation_end_date
        booking_open_date = datetime.strptime(request.form['booking_open_date'], '%Y-%m-%d').date()
        booking_close_date = datetime.strptime(request.form['booking_close_date'], '%Y-%m-%d').date()
        if booking_close_date < booking_open_date:
            return show('Booking close date must be on or after the date booking opens.')
        exam.booking_open_date = booking_open_date
        exam.booking_close_date = booking_close_date
        exam.exam_duration = int(request.form['exam_duration'])
        examinor_id = int(request.form['examinor_id'])
        user = User.query.get(examinor_id)
        exam.examinor_id = examinor_id
        exam.examinor_name = user.name
        exam.coures_id = int(request.form['course_id'])
        db.session.commit()
        return redirect(url_for('admin.manage_exams'))

    return show()


@admin_blueprint.route('/delete_exam/<int:id>', methods=['POST', 'GET'])
def delete_exam(id):
    quetionBank.query.filter_by(exam_id=id).delete()
    StudentMark.query.filter_by(exam_id=id).delete()
    ExamRemark.query.filter_by(exam_id=id).delete()
    SlotBooking.query.filter_by(exam_id=id).delete()
    ExamSlot.query.filter_by(exam_id=id).delete()
    exam = Exam.query.get(id)
    db.session.delete(exam)
    db.session.commit()
    return redirect(url_for('admin.manage_exams'))


@admin_blueprint.route('/open_booking/<int:id>')
def open_booking(id):
    exam = Exam.query.get(id)
    if exam:
        exam.is_booking_open = True
        db.session.commit()
    return redirect(url_for('admin.manage_exams'))


@admin_blueprint.route('/close_booking/<int:id>')
def close_booking(id):
    exam = Exam.query.get(id)
    if exam:
        exam.is_booking_open = False
        db.session.commit()
        return redirect(url_for('admin.manage_exams'))


@admin_blueprint.route('/publish_results/<int:id>', methods=['GET', 'POST'])
def publish_results(id):
    exam = Exam.query.get(id)
    if exam:
        exam.results_published = True
        db.session.commit()
    return redirect(url_for('admin.manage_exams'))


@admin_blueprint.route('/hide_results/<int:id>', methods=['GET', 'POST'])
def hide_results(id):
    exam = Exam.query.get(id)
    if exam:
        exam.results_published = False
        db.session.commit()
    return redirect(url_for('admin.manage_exams'))


@admin_blueprint.route('/view_bookings', methods=['GET'])
def view_bookings():
    q = _query_text()
    all_bookings = SlotBooking.query.all()
    exams = {exam.id: exam for exam in Exam.query.all()}
    students = {user.id: user for user in User.query.filter(User.role == 'student').all()}
    bookings = [
        booking for booking in all_bookings
        if _booking_matches(q, booking, exams.get(booking.exam_id), students.get(booking.student_id))
    ]
    slots = {slot.id: slot for slot in ExamSlot.query.filter(ExamSlot.id.in_([booking.slot_id for booking in bookings])).all()} if bookings else {}
    profiles = {profile.user_id: profile for profile in User_profile.query.filter(User_profile.user_id.in_([booking.student_id for booking in bookings])).all()} if bookings else {}
    return render_template(
        '/admin/view_bookings.html',
        bookings=bookings,
        exams=exams,
        slots=slots,
        students=students,
        profiles=profiles,
        q=q
    )


@admin_blueprint.route('/manage_examinors',methods=['POST','GET'])
def manage_examinors():
    q = _query_text()
    examinors = [
        user for user in User.query.filter_by(role='examinor').all()
        if _matches_name_or_id(q, user.id, user.name)
    ]
    return render_template('/admin/manage_examinors.html', examinors=examinors, q=q)


@admin_blueprint.route('/edit_examinor/<int:id>',methods=['POST','GET'])
def edit_examinor(id):
    examinor = User.query.get(id)
    return render_template('/admin/edit_examinor.html',examinor=examinor)
@admin_blueprint.route('/approve_examinor/<int:id>',methods=['POST','GET'])
def approve_examinor(id):
    examinor = User.query.get(id)
    examinor.is_verified = True
    db.session.commit()
    return redirect(url_for('admin.manage_examinors'))


@admin_blueprint.route('/manage_users',methods=['POST','GET'])
def manage_users():
    q = _query_text()
    users = [
        user for user in User.query.filter(User.role.in_(['student'])).all()
        if _matches_name_or_id(q, user.id, user.name)
    ]
    return render_template('/admin/manage_users.html', users=users, q=q)




@admin_blueprint.route('/user_details/<int:id>',methods=['GET'])
def user_details(id):
    user = User.query.get(id)
    profile = User_profile.query.filter_by(user_id=id).first()
    return render_template('/admin/user_details.html', user=user, profile=profile)


@admin_blueprint.route('/block_user/<int:id>')
def block_user(id):
    user = User.query.get(id)
    user.is_active = False
    db.session.commit()
    if user.role == 'examinor':
        return redirect(url_for('admin.manage_examinors'))
    return redirect(url_for('admin.manage_users'))


@admin_blueprint.route('/unblock_user/<int:id>')
def unblock_user(id):
    user = User.query.get(id)
    user.is_active = True
    db.session.commit()
    if user.role == 'examinor':
        return redirect(url_for('admin.manage_examinors'))
    return redirect(url_for('admin.manage_users'))