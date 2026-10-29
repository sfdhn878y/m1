

from models import *
from flask import Blueprint
admin_blueprint = Blueprint('admin',__name__)




@admin_blueprint.route('/admin_dashboard',methods=['POST','GET'])
def admin_dashboard():
    return render_template('/admin/admin_dashboard.html')



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
    course = Course.query.get(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('manage_courses'))

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

@admin_blueprint.route('/create_rubric',methods=['POST','GET'])
def create_rubric():
 
    return render_template('/admin/create_rubic.html')
