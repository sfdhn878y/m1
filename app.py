from flask import Flask,render_template,jsonify,request,session
from flask_sqlalchemy import SQLAlchemy
from flask import redirect,url_for
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'sdfsfsdfad'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from flask import Blueprint
from extension import db
from auth import auth_blueprint
from models import *
from admin import admin_blueprint

app.register_blueprint(auth_blueprint,url_prefix='/auth')
app.register_blueprint(admin_blueprint,url_prefix='/admin')

db.init_app(app)


@app.route('/logout',methods=['POST','GET'])
def logout():
    session.pop('user_id',None)
    return redirect(url_for('index'))






@app.route('/')
def index():
    return render_template('index.html')




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        old_user = User.query.filter_by(email='admin@gmail.com').first()
        if not old_user:
            new_admin = User(name='admin',email='admin@gmail.com',password='admin',role='admin')
            db.session.add(new_admin)
            db.session.commit()

    app.run(debug=True)