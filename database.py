import sqlite3
from pathlib import Path
DATABASE=Path(__file__).with_name("caselink.db")
def get_db_connection():
 c=sqlite3.connect(DATABASE); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def initialize_database():
 c=get_db_connection()
 c.executescript("""
 CREATE TABLE IF NOT EXISTS cases(id INTEGER PRIMARY KEY AUTOINCREMENT,case_number TEXT NOT NULL,title TEXT NOT NULL,description TEXT,location TEXT,case_date TEXT,status TEXT DEFAULT 'ACTIVE');
 CREATE TABLE IF NOT EXISTS suspects(id INTEGER PRIMARY KEY AUTOINCREMENT,case_id INTEGER NOT NULL,name TEXT NOT NULL,age INTEGER,occupation TEXT,last_seen TEXT,notes TEXT,FOREIGN KEY(case_id) REFERENCES cases(id));
 CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY AUTOINCREMENT,case_id INTEGER NOT NULL,title TEXT NOT NULL,evidence_type TEXT,description TEXT,location TEXT,evidence_date TEXT,FOREIGN KEY(case_id) REFERENCES cases(id));
 CREATE TABLE IF NOT EXISTS statements(id INTEGER PRIMARY KEY AUTOINCREMENT,case_id INTEGER NOT NULL,person_name TEXT NOT NULL,statement_text TEXT NOT NULL,statement_date TEXT,location TEXT,FOREIGN KEY(case_id) REFERENCES cases(id));
 CREATE TABLE IF NOT EXISTS timeline(id INTEGER PRIMARY KEY AUTOINCREMENT,case_id INTEGER NOT NULL,event_title TEXT NOT NULL,event_description TEXT,event_date TEXT NOT NULL,event_time TEXT,location TEXT,FOREIGN KEY(case_id) REFERENCES cases(id));
 """)
 c.commit(); c.close()
