import sqlite3

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
        id_soil INTEGER NOT NULL,
        phytotoxicity_mean FLOAT,
        date_time DATETIME NOT NULL,
        FOREIGN KEY (id_soil) REFERENCES Soil(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Test_control (
        id INTEGER PRIMARY KEY,
        name_test VARCHAR(100) NOT NULL,
        id_soil INTEGER NOT NULL,
        date_time DATETIME NOT NULL,
        FOREIGN KEY (id_soil) REFERENCES Soil(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Measuring (
        id INTEGER PRIMARY KEY,
        id_selection INTEGER NOT NULL,
        id_test INTEGER,
        phytotoxicity_value FLOAT,
        FOREIGN KEY (id_selection) REFERENCES Selection(id),
        FOREIGN KEY (id_test) REFERENCES Test_control(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Gauging (
        id INTEGER PRIMARY KEY,
        id_measuring INTEGER NOT NULL,
        id_feature INTEGER NOT NULL,
        score TEXT,
        FOREIGN KEY (id_measuring) REFERENCES Measuring(id),
        FOREIGN KEY (id_feature) REFERENCES Feature(id)
    );
    """)

    conn.commit()
    conn.close()

create_database()
