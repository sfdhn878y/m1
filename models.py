from extension import db
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(100),nullable=False)
    role = db.Column(db.String(100),nullable=False) # studnet , examinor , admin

    is_verified = db.Column(db.Boolean,default=False)
    is_active = db.Column(db.Boolean,default=True)

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
    slot_creation_start_date = db.Column(db.Date,nullable=True)
    slot_creation_end_date = db.Column(db.Date,nullable=True)
    booking_start_time = db.Column(db.Time,nullable=False)
    booking_end_time = db.Column(db.Time,nullable=False)
    booking_open_date = db.Column(db.Date,nullable=True)
    booking_close_date = db.Column(db.Date,nullable=True)
    is_booking_open = db.Column(db.Boolean, default=False)
    results_published = db.Column(db.Boolean, default=False)
    examinor_name = db.Column(db.String(100),nullable=False)
    coures_id = db.Column(db.Integer,db.ForeignKey('course.id'),nullable=False)
    examinor_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    users = db.relationship('User',backref='exams',lazy=True)


class ExamSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    slot_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class SlotBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('exam_slot.id'), nullable=False, unique=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class quetionBank(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    question = db.Column(db.String(100),nullable=False)
    marks = db.Column(db.Integer,nullable=False)
    exam_id = db.Column(db.Integer,db.ForeignKey('exam.id'),nullable=False)


class StudentMark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quetion_bank.id'), nullable=False)
    marks_awarded = db.Column(db.Integer, nullable=False)
    given_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class ExamRemark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    remark = db.Column(db.String(500), nullable=False)
    given_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
