from flask  import Blueprint
from flask import request
from models import User
from extension import db
from flask import redirect, render_template,url_for,session



auth_blueprint = Blueprint('auth',__name__)



@auth_blueprint.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        user = User(name=name,email=email,password=password,role=role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('/auth/register.html')


@auth_blueprint.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user.password == password:
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
        
            if user.role =='user':
                return redirect(url_for('user.user_dashboard'))
        else:
            return render_template('login.html',error='Invalid email or password')
       
    return render_template('/auth/login.html')