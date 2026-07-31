import yaml
from datetime import timedelta, date
import query.connect as connect

def insert_att(modified):
    cleaned = [
        (row[0], row[1], row[2], row[3], row[4])
        for row in modified
    ]
    connect.cursor.executemany("""
    INSERT INTO attendance (lesson_id, student_id, mark, comment, blocked)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(lesson_id, student_id)
    DO UPDATE SET
        mark = excluded.mark, comment = excluded.comment, blocked = excluded.blocked;
    """, cleaned)
    connect.db.commit()

def update_status(status, lesson_id):
    connect.cursor.execute("UPDATE timetable SET status = ? WHERE id = ?", (status, lesson_id,))
    connect.db.commit()

def insert_lesson(modified):
    connect.cursor.execute("INSERT INTO timetable (date, number, discipline, type, teacher, subgrp_type, podgroup, type_week, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", modified)
    connect.db.commit()

def insert_med(med_dict):
    connect.cursor.execute("""
        INSERT INTO med_docs
        (student_id, date_start, date_end, url)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (student_id)
        DO UPDATE SET
            date_start = excluded.date_start, date_end = excluded.date_end, url = excluded.url
    """, med_dict)
    connect.db.commit()

    connect.cursor.execute("""
        SELECT id FROM timetable WHERE date >= ? AND date <= ?
    """, (med_dict[1], med_dict[2]))
    tt_id = connect.cursor.fetchall()
    ids = [
        (lesson_id[0], med_dict[0], "б", med_dict[3], 1)
        for lesson_id in tt_id
    ]

    connect.cursor.executemany("""
        INSERT INTO attendance 
            (lesson_id, student_id, mark, comment, blocked)
        VALUES 
            (?, ?, ?, ?, ?)
    """, ids)

def insert_students(students):
    connect.cursor.execute("""
        INSERT INTO students
            (full_name, phone, birthday, status)
        VALUES
            (?, ?, ?, ?)
    """, students)
    connect.db.commit()

def update_student(student):
    connect.cursor.execute("""
        UPDATE students SET
            full_name = ?,
            phone = ?,
            birthday = ?,
            status = ?
        WHERE
            id = ?
    """, student)
    connect.db.commit()

def update_subgrps(data):
    connect.cursor.executemany("""
            INSERT INTO students_subgrps
            (student_id, type_id, subgroup)
            VALUES (?, ?, ?)
            ON CONFLICT (student_id, type_id)
            DO UPDATE SET
                student_id = excluded.student_id, type_id = excluded.type_id, subgroup = excluded.subgroup
        """, data)
    connect.db.commit()

def write_yaml(path, data):
    with open(path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)