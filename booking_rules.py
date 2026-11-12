from datetime import date

from extension import db
from models import SlotBooking


def exam_phase(exam, today=None):
    today = today or date.today()
    if not exam:
        return 'Draft'
    if exam.exam_date and exam.exam_date < today:
        return 'Completed'
    if booking_window_open(exam, today):
        return 'Booking Open'
    if getattr(exam, 'is_slot_creation_open', False):
        return 'Slot Creation'
    if exam.booking_close_date and today > exam.booking_close_date:
        return 'Closed'
    if exam.is_booking_open and exam.booking_open_date and today < exam.booking_open_date:
        return 'Booking scheduled'
    if exam.booking_open_date and today >= exam.booking_open_date:
        return 'Closed'
    return 'Draft'


def booking_window_open(exam, today=None):
    today = today or date.today()
    if not exam or not exam.is_booking_open:
        return False
    if exam.booking_close_date and today > exam.booking_close_date:
        return False
    if exam.booking_open_date and today < exam.booking_open_date:
        from models import ExamSlot
        if not ExamSlot.query.filter_by(exam_id=exam.id).first():
            return False
    return True


def active_counts():
    rows = SlotBooking.query.filter_by(status='Booked').all()
    counts = {}
    for row in rows:
        counts[row.slot_id] = counts.get(row.slot_id, 0) + 1
    return counts


def seats_taken(slot, counts=None):
    counts = active_counts() if counts is None else counts
    return counts.get(slot.id, 0)


def slot_is_full(slot, counts=None):
    return seats_taken(slot, counts) >= (slot.capacity or 1)


def refresh_slot_closed(slot, counts=None):
    slot.is_closed = slot_is_full(slot, counts)


def mark_finished_bookings(bookings, exams, slots, today=None):
    today = today or date.today()
    changed = False
    for booking in bookings:
        if booking.status != 'Booked':
            continue
        exam = exams.get(booking.exam_id)
        slot = slots.get(booking.slot_id)
        exam_done = exam and exam.exam_date and exam.exam_date < today
        slot_done = slot and slot.slot_date and slot.slot_date < today
        if exam_done or slot_done:
            booking.status = 'Completed'
            changed = True
    if changed:
        db.session.commit()


def display_status(booking):
    return booking.status if booking and booking.status else 'Booked'
