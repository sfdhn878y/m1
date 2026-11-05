from flask import Blueprint,render_template,request,redirect,url_for
from models import *
from flask import session
from extension import db

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route('/user_dashboard',methods=['POST','GET'])
def user_dashboard():
    user = User.query.get(session.get('user_id'))
    profile = User_profile.query.filter_by(user_id=session.get('user_id')).first()
    return render_template('user/user_dashboard.html', user=user, profile=profile)


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
