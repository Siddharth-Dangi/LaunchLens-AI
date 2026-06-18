import sqlite3
import json
import os

DB_NAME = "launchlens.db"

def init_db():
    """Initializes the database and creates the projects table if it doesn't exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                industry TEXT NOT NULL,
                problem TEXT NOT NULL,
                target_customer TEXT NOT NULL,
                country TEXT NOT NULL,
                validation_score INTEGER NOT NULL,
                opportunity_score INTEGER NOT NULL,
                risk_score INTEGER NOT NULL,
                data_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_project(name, industry, problem, target_customer, country, validation_score, opportunity_score, risk_score, data_dict):
    """Saves a GTM intelligence project to the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (
                name, industry, problem, target_customer, country,
                validation_score, opportunity_score, risk_score, data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, industry, problem, target_customer, country,
            validation_score, opportunity_score, risk_score, json.dumps(data_dict)
        ))
        conn.commit()
        return cursor.lastrowid

def get_all_projects():
    """Fetches list of all projects (meta info only for dashboard/history lists)."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, industry, problem, target_customer, country,
                   validation_score, opportunity_score, risk_score, created_at
            FROM projects
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_project_by_id(project_id):
    """Fetches a single project with its full generated details by ID."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, industry, problem, target_customer, country,
                   validation_score, opportunity_score, risk_score, data_json, created_at
            FROM projects
            WHERE id = ?
        """, (project_id,))
        row = cursor.fetchone()
        if row:
            project = dict(row)
            project["data"] = json.loads(project["data_json"])
            return project
        return None

def delete_project(project_id):
    """Deletes a project from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
