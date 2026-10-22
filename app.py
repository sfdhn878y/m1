from flask import Flask,render_template,jsonify,request,session
from flask_sqlalchemy import SQLAlchemy
from flask import redirect,url_for

app = Flask(__name__)
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
        user = User.query.filter_by(email=email,password=password).first()
        session['user_id'] = user.id
        if user:
            return render_template('profile.html')
        else:
            return render_template('login.html',error='Invalid email or password')
       
    return render_template('login.html')






@app.route('/')
def index():
    return render_template('mypuchui.html')





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)