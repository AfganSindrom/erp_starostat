import query.connect as connect
import query.constants as constants
from datetime import datetime, timedelta, date

def subgroup(item: int): return "Вся группа" if item == 0 else f"{item} п/группа"

def get_week_info(today: date):
    semester_day = connect.calendar['semester']['start_edu']
    
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    sum_days = (end_of_week-semester_day).days // 7
    week_type = 2 if sum_days % 2 == 0 else 1

    week = {"week_type": week_type, "start_week": start_of_week, "end_week": end_of_week}

    return week

def week(today):
    week = get_week_info(today)
    week_type = "Нечётная" if week['week_type'] == 1 else "Чётная"
    return week, week_type

def get_timetable_names():
    names = []
    items = []
    for number in connect.plan:
        name = number['discipline'] + " (" + constants.LESSON_TYPE_SMALL[number['type']] + ") (" + subgroup(number['podgroup']) + ")"
        names.append(name)
        item = {
            "name": number['discipline'],
            "subgrp_type": number['subgrp_type'],
            "subgroup": number['podgroup'],
            "type": number['type'],
            "teacher": number['teacher'],
            "hours": number['hours']
        }
        items.append(item)
    return names, items

def get_timetable_period(date_start: str, date_end: str):
    connect.cursor.execute("SELECT * FROM timetable WHERE `date` >= ? AND `date` <= ? ORDER BY `date` ASC, `number` ASC", (date_start, date_end))
    timetable = connect.cursor.fetchall()
    
    times = []

    for time in timetable:
        date = datetime.strptime(time[1], "%Y-%m-%d")
        item = {
            "day": date.weekday(),
            "time": time[2],
            "title": time[3],
            "lesson_type": constants.LESSON_TYPE_FULL[time[4]],
            "teacher": time[5],
            "subgrp_type": time[6],
            "subgroup": subgroup(time[7])
        }
        times.append(item)
    return times

def get_students_att(name: str, subgrp_type: int, subgroup: int, type: str):
    connect.cursor.execute("SELECT id, full_name FROM students ORDER BY full_name ASC")
    students = connect.cursor.fetchall()
    connect.cursor.execute("SELECT student_id FROM students_subgrps WHERE type_id = ? AND subgroup = ?", (subgrp_type, subgroup,))
    subgrp_types = connect.cursor.fetchall() if subgroup != 0 else [(student[0],) for student in students]
    connect.cursor.execute("SELECT * FROM timetable WHERE discipline = ? AND subgrp_type = ? AND podgroup = ? AND type = ? ORDER BY date ASC", (name, subgrp_type, subgroup, type,))
    timetable = connect.cursor.fetchall()
    
    attendance_map = {}

    connect.cursor.execute("SELECT student_id, lesson_id, mark, blocked FROM attendance")
    all_att = connect.cursor.fetchall()

    for student_id, lesson_id, mark, blocked in all_att:
        attendance_map[(student_id, lesson_id)] = {
            'mark': mark,
            'blocked': blocked
        }

    attendance = []

    for item in timetable:
        lesson_id = item[0]

        attendance.append({
            "lesson_id": lesson_id,
            "date": item[1],
            "marks": attendance_map
        })

    return students, subgrp_types, timetable, attendance

def get_all_students():
    connect.cursor.execute("SELECT id, full_name, phone, birthday, status FROM students ORDER BY full_name ASC")
    return connect.cursor.fetchall()

def get_student(id):
    connect.cursor.execute("SELECT full_name, phone, birthday, status FROM students WHERE id=?", (id,))
    return connect.cursor.fetchall()

def get_med():
    connect.cursor.execute("SELECT id, student_id, date_start, date_end, url FROM med_docs ORDER BY date_start ASC")
    med_data = connect.cursor.fetchall()

    connect.cursor.execute("SELECT id, full_name FROM students ORDER BY full_name ASC")
    students = connect.cursor.fetchall()
    students_new = {}
    for student in students: students_new[student[0]] = student[1]

    return med_data, students_new

def get_med_item(id):
    print(type(id))
    connect.cursor.execute("SELECT student_id, date_start, date_end, url FROM med_docs WHERE id = ?", str(id))
    return connect.cursor.fetchall()

def get_subgrps():
    connect.cursor.execute("SELECT id, full_name FROM students ORDER BY id ASC")
    students = connect.cursor.fetchall()

    connect.cursor.execute("SELECT id, name FROM subgrp_types ORDER BY id ASC")
    subgrp_types = connect.cursor.fetchall()

    connect.cursor.execute("SELECT student_id, type_id, subgroup FROM students_subgrps")
    subgrp = connect.cursor.fetchall()

    subgrp_data = {}

    for student_id, type_id, subgroup in subgrp:
        subgrp_data[(student_id, type_id)] = {'mark': subgroup}

    return students, subgrp_types, subgrp_data