import os
import json
import uuid

import streamlit as st
import numpy as np
import cv2
import mediapipe as mp

from pages.helper.data_models import PublicSubmissions
from pages.helper import db_queries


st.set_page_config(
    page_title="Public Submission",
    page_icon="🌍",
    layout="centered"
)


# =========================================================
# FACE DETECTION / FACE MESH
# =========================================================

@st.cache_resource
def load_face_mesh():
    return mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    )


def get_face_mesh(image):

    try:
        image_np = np.array(image)

        # Convert RGB to BGR for OpenCV
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        # Convert BGR to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        face_mesh = load_face_mesh()

        results = face_mesh.process(image_rgb)

        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark

        face_data = []

        for landmark in landmarks:
            face_data.append({
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
            })

        return face_data

    except Exception as e:
        st.error(f"Face detection failed: {e}")
        return None


# =========================================================
# PAGE UI
# =========================================================

st.title("🌍 Public Missing Person Submission")

st.write(
    """
    If you have seen or found a person who may match a missing person case,
    please submit their information below.
    """
)

st.info(
    "Please upload a clear, front-facing photo where the person's face is visible."
)


# Back button
if st.button("← Back to Login"):
    st.switch_page("Home.py")


st.divider()


# =========================================================
# FORM
# =========================================================

with st.form("public_submission_form"):

    submitted_by = st.text_input(
        "Your Name",
        max_chars=128
    )

    mobile = st.text_input(
        "Your Mobile Number",
        max_chars=10
    )

    email = st.text_input(
        "Your Email (Optional)"
    )

    location = st.text_input(
        "Location where the person was seen",
        max_chars=128
    )

    birth_marks = st.text_area(
        "Birth Marks / Identification Marks (Optional)",
        max_chars=512
    )

    uploaded_file = st.file_uploader(
        "Upload Person's Photo",
        type=["jpg", "jpeg", "png"]
    )

    submit_button = st.form_submit_button(
        "📤 Submit Information",
        width="stretch"
    )


# =========================================================
# SUBMISSION LOGIC
# =========================================================

if submit_button:

    # Validation
    if not submitted_by.strip():
        st.error("Please enter your name.")

    elif not mobile.strip():
        st.error("Please enter your mobile number.")

    elif len(mobile.strip()) != 10 or not mobile.strip().isdigit():
        st.error("Please enter a valid 10-digit mobile number.")

    elif not location.strip():
        st.error("Please enter the location.")

    elif uploaded_file is None:
        st.error("Please upload a photo.")

    else:

        with st.spinner("Processing face..."):

            # Read image
            file_bytes = np.asarray(
                bytearray(uploaded_file.read()),
                dtype=np.uint8
            )

            image = cv2.imdecode(
                file_bytes,
                cv2.IMREAD_COLOR
            )

            image_rgb = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            )

            # Extract face landmarks
            face_mesh = get_face_mesh(image_rgb)

        if face_mesh is None:

            st.error("❌ No face detected in this image.")

            st.warning(
                "Tips: Use a well-lit, front-facing photo with one clear face visible."
            )

        else:

            try:

                # Create unique ID
                submission_id = str(uuid.uuid4())

                # Create resources directory
                os.makedirs("resources", exist_ok=True)

                # Save image
                image_extension = uploaded_file.name.split(".")[-1]

                image_path = os.path.join(
                    "resources",
                    f"{submission_id}.{image_extension}"
                )

                with open(image_path, "wb") as f:
                    f.write(file_bytes)

                # Save in database
                submission = PublicSubmissions(
                    id=submission_id,
                    submitted_by=submitted_by.strip(),
                    face_mesh=json.dumps(face_mesh),
                    location=location.strip(),
                    mobile=mobile.strip(),
                    email=email.strip() if email.strip() else None,
                    status="Pending",
                    birth_marks=birth_marks.strip()
                    if birth_marks.strip()
                    else None,
                )

                db_queries.add_public_submission(submission)

                st.success(
                    "✅ Information submitted successfully!"
                )

                st.info(
                    "Thank you for helping us identify missing persons."
                )

            except Exception as e:

                st.error(
                    f"❌ Failed to submit information: {e}"
                )