
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def create_tables():
    with connect_db() as conn:
        with conn.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detection_sessions (
                    id SERIAL PRIMARY KEY,
                    started_at TIMESTAMPTZ DEFAULT NOW(),
                    ended_at TIMESTAMPTZ
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detected_objects (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES detection_sessions(id),
                    track_id INTEGER NOT NULL,
                    object_name VARCHAR(100) NOT NULL,
                    confidence FLOAT NOT NULL,
                    detected_at TIMESTAMPTZ DEFAULT NOW(),

                    UNIQUE(session_id, track_id)
                );
            """)

    print("Database tables are ready.")


def start_session():
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO detection_sessions DEFAULT VALUES
                RETURNING id;
            """)

            session_id = cursor.fetchone()[0]

    print(f"Detection session started: {session_id}")

    return session_id


def save_detections(session_id, detections):
    if not detections:
        return

    records = [
        (
            session_id,
            item["track_id"],
            item["object"],
            item["confidence"]
        )
        for item in detections
        if item["track_id"] is not None
    ]

    if not records:
        return

    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO detected_objects (
                    session_id,
                    track_id,
                    object_name,
                    confidence
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (session_id, track_id)
                DO NOTHING;
            """, records)


def end_session(session_id):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE detection_sessions
                SET ended_at = NOW()
                WHERE id = %s;
            """, (session_id,))

    print(f"Detection session {session_id} ended.")
