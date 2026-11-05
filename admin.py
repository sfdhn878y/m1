

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



@admin_blueprint.route('/manage_exams',methods=['POST','GET'])
def manage_exams():
    exams = Exam.query.all()
    return render_template('/admin/manage_exams.html',exams=exams)


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

        booking_start_time = datetime.strptime(
            request.form['booking_start_time'], '%H:%M'
        ).time()

        booking_end_time = datetime.strptime(
            request.form['booking_end_time'], '%H:%M'
        ).time()

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
            booking_start_time=booking_start_time,
            booking_end_time=booking_end_time,
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
    db.session.delete(rubric)
    db.session.commit()
    return redirect(url_for('admin.manage_rubric', id=exam_id))


@admin_blueprint.route('/edit_exam/<int:id>', methods=['POST', 'GET'])
def edit_exam(id):
    exam = Exam.query.get(id)
    examinors = User.query.filter_by(role='examinor').all()
    courses = Course.query.all()

    if request.method == 'POST':
        exam.exam_name = request.form['exam_name']
        exam.exam_description = request.form['exam_description']
        exam.exam_date = datetime.strptime(request.form['exam_date'], '%Y-%m-%d').date()
        exam.exam_time = datetime.strptime(request.form['exam_time'], '%H:%M').time()
        exam.slot_start_time = datetime.strptime(request.form['slot_start_time'], '%H:%M').time()
        exam.slot_end_time = datetime.strptime(request.form['slot_end_time'], '%H:%M').time()
        exam.booking_start_time = datetime.strptime(request.form['booking_start_time'], '%H:%M').time()
        exam.booking_end_time = datetime.strptime(request.form['booking_end_time'], '%H:%M').time()
        exam.exam_duration = int(request.form['exam_duration'])
        examinor_id = int(request.form['examinor_id'])
        user = User.query.get(examinor_id)
        exam.examinor_id = examinor_id
        exam.examinor_name = user.name
        exam.coures_id = int(request.form['course_id'])
        db.session.commit()
        return redirect(url_for('admin.manage_exams'))

    return render_template(
        '/admin/edit_exam.html',
        exam=exam,
        examinors=examinors,
        courses=courses
    )


@admin_blueprint.route('/delete_exam/<int:id>', methods=['POST', 'GET'])
def delete_exam(id):
    quetionBank.query.filter_by(exam_id=id).delete()
    exam = Exam.query.get(id)
    db.session.delete(exam)
    db.session.commit()
    return redirect(url_for('admin.manage_exams'))



@admin_blueprint.route('/manage_examinors',methods=['POST','GET'])
def manage_examinors():
    examinors = User.query.filter_by(role='examinor').all()
    return render_template('/admin/manage_examinors.html',examinors=examinors)


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
    users = User.query.filter(User.role.in_(['student'])).all()
    return render_template('/admin/manage_users.html', users=users)




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