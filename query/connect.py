import sqlite3
import yaml
import sys
import re
from pathlib import Path
import query.constants as constants

with open("config.yml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

def check_dir(folder_name):
    pattern = r"(spring|autumn)_\d{4}"
    for item in folder_name.iterdir():
        if re.search(pattern, str(item)):
            folder_item = Path(item)
            if (folder_item / "semester.db").is_file() and (folder_item / "plan.yml").is_file() and (folder_item / "calendar.yml").is_file() and (folder_item / "timetable.yml").is_file():
                return True

def get_names(folder_name):
    names = []
    if check_dir(folder_name):
        for item in folder_name.iterdir():
            pattern = r"(?P<season>spring|autumn)_(?P<year_start>\d{2})(?P<year_end>\d{2})"
            match = re.search(pattern, str(item))
            if match:
                season = match.group("season")
                year_start = match.group("year_start")
                year_end = match.group("year_end")
                names.append({'folder_path': str(item), 'season': season, 'year_start': year_start, 'year_end': year_end})
    return names

def get_semester_data(folder_path: str):
    db = sqlite3.connect(folder_path + "/semester.db")
    cursor = db.cursor()

    with open(folder_path + '/calendar.yml', "r", encoding="utf-8") as file:
        calendar = yaml.safe_load(file)
    with open(folder_path + '/plan.yml', "r", encoding="utf-8") as file:
        plan = yaml.safe_load(file)
    with open(folder_path + '/timetable.yml', "r", encoding="utf-8") as file:
        timetable = yaml.safe_load(file)
    
    return db, cursor, calendar, plan, timetable

names = get_names(constants.FOLDER)
for item in names:
    name = item['season']+"_"+item['year_start']+item['year_end']
    if name in config['config']['current']:
        db, cursor, calendar, plan, timetable = get_semester_data(item['folder_path'])
        break