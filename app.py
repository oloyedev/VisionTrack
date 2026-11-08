
import streamlit as st
import pandas as pd
import psycopg
import os

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="VisionTrack",
    page_icon="👁️",
    layout="wide"
)




def connect_db():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )




def fetch_data(query):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)

            columns = [
                description.name
                for description in cursor.description
            ]

            rows = cursor.fetchall()

    return pd.DataFrame(rows, columns=columns)




def get_overview():
    query = """
        SELECT
            COUNT(DISTINCT s.id) AS total_sessions,
            COUNT(d.id) AS total_objects,
            COUNT(DISTINCT d.object_name) AS categories
        FROM detection_sessions s
        LEFT JOIN detected_objects d
        ON s.id = d.session_id;
    """

    return fetch_data(query)


def get_category_summary():
    query = """
        SELECT
            object_name,
            COUNT(*) AS total
        FROM detected_objects
        GROUP BY object_name
        ORDER BY total DESC;
    """

    return fetch_data(query)


def get_recent_detections():
    query = """
        SELECT
            d.id,
            d.object_name,
            d.track_id,
            ROUND(d.confidence::numeric, 2) AS confidence,
            d.detected_at,
            d.session_id
        FROM detected_objects d
        ORDER BY d.detected_at DESC
        LIMIT 20;
    """

    return fetch_data(query)


def get_sessions():
    query = """
        SELECT
            s.id,
            s.started_at,
            s.ended_at,
            COUNT(d.id) AS objects_detected
        FROM detection_sessions s
        LEFT JOIN detected_objects d
        ON s.id = d.session_id
        GROUP BY s.id
        ORDER BY s.started_at DESC;
    """

    return fetch_data(query)




st.title("VisionTrack")
st.caption("AI-Powered Object Detection and Tracking System")

if st.button("Refresh dashboard"):
    st.rerun()


try:
    overview = get_overview()
    categories = get_category_summary()
    recent = get_recent_detections()
    sessions = get_sessions()

  

    st.subheader("System Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Detection Sessions",
        int(overview.iloc[0]["total_sessions"])
    )

    col2.metric(
        "Unique Objects Detected",
        int(overview.iloc[0]["total_objects"])
    )

    col3.metric(
        "Object Categories",
        int(overview.iloc[0]["categories"])
    )

    st.divider()



    st.subheader("Object Detection Analytics")

    left, right = st.columns(2)

    with left:
        st.write("Most Detected Objects")

        if not categories.empty:
            st.bar_chart(
                categories.set_index("object_name")["total"]
            )
        else:
            st.info("No detection records available yet.")

    with right:
        st.write("Category Breakdown")

        if not categories.empty:
            st.dataframe(
                categories,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Waiting for detection data.")

    st.divider()



    st.subheader("Recent Detection Records")

    if not recent.empty:
        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No objects have been detected yet.")

    st.divider()

    

    st.subheader("Detection Session History")

    if not sessions.empty:
        st.dataframe(
            sessions,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No detection sessions found.")

except Exception as error:
    st.error(f"Database connection error: {error}")
