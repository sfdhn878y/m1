from flask import Flask,render_template,jsonify,request,session
from flask_sqlalchemy import SQLAlchemy
from flask import redirect,url_for
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'sdfsfsdfad'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(100),nullable=False)
    role = db.Column(db.String(100),nullable=False) # studnet , examinor , admin




class User_profile(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    address = db.Column(db.String(100),nullable=False)
    phone = db.Column(db.String(100),nullable=False)
    past_experience = db.Column(db.String(100),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,unique=True)


class Staff_Profile(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    address = db.Column(db.String(100),nullable=False)
    phone = db.Column(db.String(100),nullable=False)
    past_experience = db.Column(db.String(100),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,unique=True)



class Course(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    coures_name = db.Column(db.String(100),nullable=False)
    coures_description = db.Column(db.String(100),nullable=False)
    course_duration = db.Column(db.Integer,nullable=False)




class Exam(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    exam_name = db.Column(db.String(100),nullable=False)
    exam_description = db.Column(db.String(100),nullable=False)
    exam_date = db.Column(db.Date,nullable=False)
    exam_time = db.Column(db.Time,nullable=False)
    exam_duration = db.Column(db.Integer,nullable=False)
    slot_start_time = db.Column(db.Time,nullable=False)
    slot_end_time = db.Column(db.Time,nullable=False)
    booking_start_time = db.Column(db.Time,nullable=False)
    booking_end_time = db.Column(db.Time,nullable=False)
    examinor_name = db.Column(db.String(100),nullable=False)
    coures_id = db.Column(db.Integer,db.ForeignKey('course.id'),nullable=False)
    examinor_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    users = db.relationship('User',backref='exams',lazy=True)


class quetionBank(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    question = db.Column(db.String(100),nullable=False)
    marks = db.Column(db.Integer,nullable=False)
    exam_id = db.Column(db.Integer,db.ForeignKey('exam.id'),nullable=False)

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        user = User(name=name,email=email,password=password,role=role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user.password == password:
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        
       
        else:
            return render_template('login.html',error='Invalid email or password')
       
    return render_template('login.html')

@app.route('/logout',methods=['POST','GET'])
def logout():
    session.pop('user_id',None)
    return redirect(url_for('index'))

@app.route('/admin_dashboard',methods=['POST','GET'])
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/manage_courses',methods=['POST','GET'])
def manage_courses():
    courses = Course.query.all()
    print(courses)
  
    return render_template('manage_courses.html',courses=courses)

@app.route('/manage_exams',methods=['POST','GET'])
def manage_exams():
    exams = Exam.query.all()
    return render_template('manage_exams.html',exams=exams)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edit_course/<int:id>',methods=['POST','GET'])
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
        return redirect(url_for('admin_dashboard'))
    course = Course.query.get(id)
    return render_template('edit_course.html',course=course)

@app.route('/create_course',methods=['POST','GET'])
def create_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_description = request.form['course_description']
        course_duration = request.form['course_duration']
        course = Course(coures_name=course_name,coures_description=course_description,course_duration=course_duration)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('create_course.html')

@app.route('/delete/<int:id>',methods=['POST','GET'])
def delete(id):
    course = Course.query.get(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('manage_courses'))

from datetime import datetime
from flask import request, render_template, redirect, url_for

@app.route('/create_exam', methods=['POST', 'GET'])
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

        return redirect(url_for('admin_dashboard'))

    return render_template(
        'create_exam.html',
        examinors=examinors,
        courses=courses
    )

@app.route('/create_rubric',methods=['POST','GET'])
def create_rubric():
 
    return render_template('create_rubic.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        old_user = User.query.filter_by(email='admin@gmail.com').first()
        if not old_user:
            new_admin = User(name='admin',email='admin@gmail.com',password='admin',role='admin')
            db.session.add(new_admin)
            db.session.commit()

    app.run(debug=True)