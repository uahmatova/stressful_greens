# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "stressfull_greens.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Feature (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Soil (
        id INTEGER PRIMARY KEY,
        soil_value VARCHAR(100) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Selection (
        id INTEGER PRIMARY KEY,
        name_selection VARCHAR(100) NOT NULL,
        id_soil INTEGER,
        phytotoxicity_mean FLOAT,
        date_time DATETIME NOT NULL,
        FOREIGN KEY (id_soil) REFERENCES Soil(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Test_control (
        id INTEGER PRIMARY KEY,
        name_test VARCHAR(100) NOT NULL,
        id_soil INTEGER,
        date_time DATETIME NOT NULL,
        FOREIGN KEY (id_soil) REFERENCES Soil(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Measuring (
        id INTEGER PRIMARY KEY,
        id_selection INTEGER,
        id_test INTEGER,
        phytotoxicity_value FLOAT,
        FOREIGN KEY (id_selection) REFERENCES Selection(id),
        FOREIGN KEY (id_test) REFERENCES Test_control(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Gauging (
        id INTEGER PRIMARY KEY,
        id_measuring INTEGER,
        id_feature INTEGER,
        score TEXT,
        FOREIGN KEY (id_measuring) REFERENCES Measuring(id),
        FOREIGN KEY (id_feature) REFERENCES Feature(id)
    );
    """)

    conn.commit()
    conn.close()

def insert_test_data():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Добавляем почвы (Soil), включая "Суглинок"
    soils = ["Суглинок", "Pb 1 ОДК", "Pb 0,5 ОДК", "Pb 0,75 ОДК"]
    for soil in soils:
        cursor.execute("INSERT INTO Soil (soil_value) VALUES (?)", (soil,))

    # Получаем id почвы "Суглинок"
    cursor.execute("SELECT id FROM Soil WHERE soil_value = ?", ("Суглинок",))
    suglinok_id = cursor.fetchone()[0]

    # 2. Добавляем характеристики (Feature) — длина стебля в сантиметрах (float), в колонку name
    for _ in range(10):
        length = round(random.uniform(1.0, 13.0), 2)
        cursor.execute("INSERT INTO Feature (name) VALUES (?)", (str(length),))

    # 3. Добавляем выборки Selection (все на "Суглинок")
    for i in range(5):
        cursor.execute("""
            INSERT INTO Selection (name_selection, id_soil, phytotoxicity_mean, date_time)
            VALUES (?, ?, ?, ?)
        """, (
            f"Selection {i+1}",
            suglinok_id,
            round(random.uniform(0, 10), 2),
            (datetime.now() - timedelta(days=i)).isoformat()
        ))

    # 4. Добавляем тесты Test_control (все на "Суглинок")
    for i in range(5):
        cursor.execute("""
            INSERT INTO Test_control (name_test, id_soil, date_time)
            VALUES (?, ?, ?)
        """, (
            f"Control {chr(65 + i)}",
            suglinok_id,
            (datetime.now() - timedelta(days=i)).isoformat()
        ))

    # Получаем id всех выборок и тестов для связи в Measuring
    cursor.execute("SELECT id FROM Selection")
    selection_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM Test_control")
    test_ids = [row[0] for row in cursor.fetchall()]

    # 5. Добавляем измерения Measuring
    # По 5 для выборок (id_test = None) и 5 для тестов (id_selection = None) — всего 10 записей
    for sel_id in selection_ids:
        cursor.execute("""
            INSERT INTO Measuring (id_selection, id_test, phytotoxicity_value)
            VALUES (?, ?, ?)
        """, (
            sel_id,
            None,
            round(random.uniform(0, 10), 2)
        ))
    for test_id in test_ids:
        cursor.execute("""
            INSERT INTO Measuring (id_selection, id_test, phytotoxicity_value)
            VALUES (?, ?, ?)
        """, (
            None,
            test_id,
            round(random.uniform(0, 10), 2)
        ))

    # Получаем id всех измерений
    cursor.execute("SELECT id FROM Measuring")
    measuring_ids = [row[0] for row in cursor.fetchall()]

    # Получаем id всех характеристик
    cursor.execute("SELECT id FROM Feature")
    feature_ids = [row[0] for row in cursor.fetchall()]

    # 6. Добавляем Gauging — по 2 уникальных оценки (характеристики) для каждого измерения
    used_features = set()
    for measuring_id in measuring_ids:
        available_features = list(set(feature_ids) - used_features)
        count_to_choose = min(2, len(available_features))
        if count_to_choose == 0:
            # Если все характеристики уже использованы, сбрасываем used_features, чтобы не остановить вставку
            used_features.clear()
            available_features = list(feature_ids)
            count_to_choose = 2 if len(available_features) >= 2 else len(available_features)
        chosen_features = random.sample(available_features, count_to_choose)
        used_features.update(chosen_features)

        for fid in chosen_features:
            # Получаем длину стебля из Feature (name)
            cursor.execute("SELECT name FROM Feature WHERE id = ?", (fid,))
            length = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO Gauging (id_measuring, id_feature, score)
                VALUES (?, ?, ?)
            """, (
                measuring_id,
                fid,
                length
            ))

    conn.commit()
    conn.close()


def print_table(title, columns, rows):
    print(f"\n=== {title} ===")
    print(" | ".join(columns))
    print("-" * (len(columns) * 15))
    for row in rows:
        print(" | ".join(str(x) for x in row))


def print_all_data():
    conn = get_connection()
    cursor = conn.cursor()

    tables = {
        "Soil": ("id, soil_value", "SELECT id, soil_value FROM Soil"),
        "Feature": ("id, name", "SELECT id, name FROM Feature"),
        "Selection": ("id, name_selection, id_soil, phytotoxicity_mean, date_time",
                      "SELECT id, name_selection, id_soil, phytotoxicity_mean, date_time FROM Selection"),
        "Test_control": ("id, name_test, id_soil, date_time",
                         "SELECT id, name_test, id_soil, date_time FROM Test_control"),
        "Measuring": ("id, id_selection, id_test, phytotoxicity_value",
                      "SELECT id, id_selection, id_test, phytotoxicity_value FROM Measuring"),
        "Gauging": ("id, id_measuring, id_feature, score",
                    "SELECT id, id_measuring, id_feature, score FROM Gauging"),
    }

    for table_name, (columns, query) in tables.items():
        cursor.execute(query)
        rows = cursor.fetchall()
        print_table(table_name, columns.split(", "), rows)

    conn.close()


if __name__ == "__main__":
    create_database()
    insert_test_data()
    print_all_data()

