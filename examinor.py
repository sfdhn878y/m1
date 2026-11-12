from flask import Blueprint,render_template,request,redirect,url_for
from models import *
from flask import session
from extension import db

examior_blueprint = Blueprint("examior", __name__)


@examior_blueprint.route('/examior_dashboard',methods=['POST','GET'])
def examior_dashboard():
    user = User.query.get(session.get('user_id'))
    profile = Staff_Profile.query.filter_by(user_id=session.get('user_id')).first()
    return render_template('examior/examior_dashboard.html', user=user, profile=profile)


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