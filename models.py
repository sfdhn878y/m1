from extension import db
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
