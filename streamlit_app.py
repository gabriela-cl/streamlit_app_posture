import streamlit as st
import numpy as np
from PIL import Image
import mediapipe as mp
import ergonomic_recommendations_streamlit
import cv2
import joblib

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)
mp_drawing = mp.solutions.drawing_utils

# Load the saved model
loaded_model = joblib.load('best_logistic_model.pkl')

# Title of the app
st.title("Ergonomic Recommendations: Set Up Your Workplace")

# Introductory information
st.subheader("First, we will need some information:")

# Ask the user if they have an adjustable desk
desk_adj = st.radio("Do you have an adjustable desk?", ('yes', 'no'))

# Instructions for the picture
st.subheader("Now, we will need a picture of you sitting at your work desk:")

st.write("Please make sure that your hips are as back as possible on the chair seat.")
st.write("Your back is straight, as tall as possible.")
st.write("Your feet are directly under your knee and resting on the floor.")
st.write("Keep your elbows close to your body and the wrists resting on the table.")
st.write("Take a picture from the side, try to NOT take it from a diagonal angle.")

# Display an example image
example_image_path = 'sitting_recommendations.png'  # Path to your example image
example_image = Image.open(example_image_path)
st.image(example_image, caption='Example: Correct Sitting Posture', use_column_width=True)

# File uploader for the user's picture
uploaded_file = st.file_uploader("Upload an image of yourself at your desk", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    try:
        # Load the uploaded image
        image = Image.open(uploaded_file)
        image_np = np.array(image)

        # Flip the image vertically to match coordinate system
        image_np_flipped = np.flipud(image_np)

        # Process the image to find pose landmarks
        results = pose.process(cv2.cvtColor(image_np_flipped, cv2.COLOR_RGB2BGR))

        # Draw pose landmarks on the image
        if results.pose_landmarks:
            # Convert to BGR format for OpenCV drawing
            image_with_landmarks = cv2.cvtColor(image_np_flipped, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(image_with_landmarks, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # Convert back to RGB format and flip vertically to display correctly
            image_with_landmarks = cv2.cvtColor(image_with_landmarks, cv2.COLOR_BGR2RGB)
            image_with_landmarks = np.flipud(image_with_landmarks)

            # Display the image with landmarks
            st.image(image_with_landmarks, caption='Image with Pose Landmarks', use_column_width=True)

        # Function to calculate the angle between three points
        def calculate_angle(a, b, c):
            a = np.array(a)
            b = np.array(b)
            c = np.array(c)
            ba = a - b
            bc = c - b
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(cosine_angle)
            return np.degrees(angle)

        # Extract keypoints (landmarks) and calculate angles if landmarks are detected
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Extract left landmarks
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Extract right landmarks
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

            # Calculate angles for the left side
            left_hip_angle = calculate_angle(left_shoulder, left_hip, left_knee)
            left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
            left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

            # Calculate angles for the right side
            right_hip_angle = calculate_angle(right_shoulder, right_hip, right_knee)
            right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
            right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

            # Determine which side is more visible based on confidence scores
            left_visibility = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility
            right_visibility = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility
            
            st.subheader("Here are your results & recommendations:")

            if left_visibility > right_visibility:
                hip_angle = left_hip_angle
                knee_angle = left_knee_angle
                elbow_angle = left_elbow_angle

                st.write(f'The recommended Hip Angle is between 90 & 120 degrees. Your current angle is: {left_hip_angle:.2f} degrees')
                st.write(f'The recommended Knee Angle is between 90 & 130 degrees. Your current angle is: {left_knee_angle:.2f} degrees')
                st.write(f'The recommended Elbow Angle is between 90 & 120 degrees. Your current angle is: {left_elbow_angle:.2f} degrees')
            else:
                hip_angle = right_hip_angle
                knee_angle = right_knee_angle
                elbow_angle = right_elbow_angle

                st.write(f'The recommended Hip Angle is between 90 & 120 degrees. Your current angle is: {right_hip_angle:.2f} degrees')
                st.write(f'The recommended Knee Angle is between 90 & 130 degrees. Your current angle is: {right_knee_angle:.2f} degrees')
                st.write(f'The recommended Elbow Angle is between 90 & 120 degrees. Your current angle is: {right_elbow_angle:.2f} degrees')

            # Call the appropriate function based on the desk type
            if desk_adj == 'yes':
                result = ergonomic_recommendations_streamlit.ergonomic_analysis_adjustable_desk(elbow_angle, hip_angle, knee_angle)
            elif desk_adj == 'no':
                result = ergonomic_recommendations_streamlit.ergonomic_analysis_fixed_desk(elbow_angle, hip_angle, knee_angle)
            
            # Display the recommendations
            for recommendation in result:
                st.write(recommendation)

    except Exception as e:
        st.error(f"An error occurred: {e}")