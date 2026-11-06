from flask import Flask,render_template,session
from flask import redirect,url_for
from sqlalchemy import text
app = Flask(__name__)
app.secret_key = 'sdfsfsdfad'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from extension import db
from auth import auth_blueprint
from models import *
from admin import admin_blueprint
from examinor import examior_blueprint
from user import user_blueprint
app.register_blueprint(auth_blueprint,url_prefix='/auth')
app.register_blueprint(admin_blueprint,url_prefix='/admin')
app.register_blueprint(examior_blueprint,url_prefix='/examior')
app.register_blueprint(user_blueprint,url_prefix='/user')
db.init_app(app)


@app.route('/logout',methods=['POST','GET'])
def logout():
    session.pop('user_id',None)
    return redirect(url_for('index'))






@app.route('/')
def index():
    return render_template('index.html')




def ensure_schema():
    db.create_all()
    exam_columns = {row[1] for row in db.session.execute(text('PRAGMA table_info(exam)'))}
    if 'slot_creation_start_date' not in exam_columns:
        db.session.execute(text('ALTER TABLE exam ADD COLUMN slot_creation_start_date DATE'))
    if 'slot_creation_end_date' not in exam_columns:
        db.session.execute(text('ALTER TABLE exam ADD COLUMN slot_creation_end_date DATE'))
    if 'booking_open_date' not in exam_columns:
        db.session.execute(text('ALTER TABLE exam ADD COLUMN booking_open_date DATE'))
    if 'booking_close_date' not in exam_columns:
        db.session.execute(text('ALTER TABLE exam ADD COLUMN booking_close_date DATE'))
    if 'is_booking_open' not in exam_columns:
        db.session.execute(text('ALTER TABLE exam ADD COLUMN is_booking_open BOOLEAN NOT NULL DEFAULT 0'))
    if 'results_published' not in exam_columns:
        db.session.execute(text('ALTER TABLE exam ADD COLUMN results_published BOOLEAN NOT NULL DEFAULT 0'))
    slot_columns = {row[1] for row in db.session.execute(text('PRAGMA table_info(exam_slot)'))}
    if slot_columns and 'slot_date' not in slot_columns:
        db.session.execute(text('DROP TABLE exam_slot'))
    db.session.commit()
    db.create_all()


if __name__ == '__main__':
    with app.app_context():
        ensure_schema()
        old_user = User.query.filter_by(email='admin@gmail.com').first()
        if not old_user:
            new_admin = User(name='admin',email='admin@gmail.com',password='admin',role='admin')
            db.session.add(new_admin)
            db.session.commit()

    app.run(debug=True)