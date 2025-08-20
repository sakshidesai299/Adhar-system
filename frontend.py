import streamlit as st
import pandas as pd
from backend import (
    create_citizen, read_citizens, update_citizen, delete_citizen,
    authenticate, get_dashboard_metrics, get_enrollment_history,
    get_authentication_log, get_deduplication_log, read_citizen_by_aadhaar_id,
    setup_database
)

# --- App Initialization ---
st.set_page_config(
    page_title="Aadhaar Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar Navigation ---
st.sidebar.title("Aadhaar System Menu")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Enrollment Management", "Authentication", "Business Insights"]
)
st.sidebar.markdown("---")
if st.sidebar.button("Setup Database"):
    setup_database()

# --- Page: Dashboard ---
if page == "Dashboard":
    st.title("📊 Dynamic Dashboard")
    st.markdown("---")

    metrics = get_dashboard_metrics()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Enrolled Citizens", metrics.get('total_enrollments', 0))
    col2.metric("Total Authentication Attempts", metrics.get('total_auth_attempts', 0))
    col3.metric("Successful Authentications", metrics.get('successful_auths', 0))

    st.markdown("### Authentication Status")
    auth_chart_data = pd.DataFrame({
        'Status': ['Successful', 'Failed'],
        'Count': [metrics.get('successful_auths', 0), metrics.get('failed_auths', 0)]
    })
    st.bar_chart(auth_chart_data.set_index('Status'))

    st.markdown("### Alerts")
    if metrics.get('recent_failed_auths', 0) > 5:
        st.error(f"🚨 ALERT: {metrics['recent_failed_auths']} failed authentication attempts in the last hour. Potential security issue!")
    if metrics.get('dedup_conflicts', 0) > 0:
        st.warning(f"⚠️ WARNING: {metrics['dedup_conflicts']} de-duplication conflicts detected. Check business insights for details.")

# --- Page: Enrollment Management ---
elif page == "Enrollment Management":
    st.title("📝 Enrollment Management")
    st.markdown("---")

    # CRUD forms
    st.header("Create New Citizen Record")
    with st.form("enrollment_form"):
        aadhaar_id = st.text_input("Aadhaar ID (12 digits)")
        name = st.text_input("Full Name")
        dob = st.date_input("Date of Birth")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        address = st.text_area("Address")
        biometric_id = st.text_input("Biometric ID (Simulated)")
        submitted = st.form_submit_button("Enroll Citizen")

        if submitted:
            if create_citizen(aadhaar_id, name, dob, gender, address, biometric_id):
                st.success("✅ Citizen enrolled successfully!")
            else:
                st.error("❌ Enrollment failed. Check the logs.")

    st.markdown("---")
    st.header("Update Citizen's Details")
    aadhaar_to_update = st.text_input("Enter Aadhaar ID to Update")
    if st.button("Load Details"):
        citizen_record = read_citizen_by_aadhaar_id(aadhaar_to_update)
        if citizen_record:
            with st.form("update_form"):
                new_name = st.text_input("Name", value=citizen_record[1])
                new_dob = st.date_input("Date of Birth", value=citizen_record[2])
                new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(citizen_record[3]))
                new_address = st.text_area("Address", value=citizen_record[4])
                if st.form_submit_button("Update Citizen"):
                    if update_citizen(aadhaar_to_update, new_name, new_dob, new_gender, new_address):
                        st.success("✅ Citizen details updated successfully!")
                    else:
                        st.error("❌ Update failed.")
        else:
            st.warning("Citizen not found.")

    st.markdown("---")
    st.header("Citizen Records")
    citizen_records = read_citizens()
    citizen_df = pd.DataFrame(citizen_records, columns=["Aadhaar ID", "Name", "Date of Birth", "Gender", "Address", "Biometric ID", "Enrollment Date"])
    st.dataframe(citizen_df, height=300)

# --- Page: Authentication ---
elif page == "Authentication":
    st.title("🔐 Authentication & eKYC")
    st.markdown("---")

    st.header("Authenticate a Citizen")
    aadhaar_auth = st.text_input("Aadhaar ID for Authentication")
    biometric_auth = st.text_input("Biometric ID for Authentication (Simulated)")
    
    if st.button("Authenticate"):
        success, message = authenticate(aadhaar_auth, biometric_auth)
        if success:
            st.success(message)
            st.markdown("---")
            st.subheader("eKYC Data (Simulated)")
            citizen_data = read_citizen_by_aadhaar_id(aadhaar_auth)
            if citizen_data:
                st.write(f"**Name:** {citizen_data[1]}")
                st.write(f"**Date of Birth:** {citizen_data[2]}")
                st.write(f"**Address:** {citizen_data[4]}")
        else:
            st.error(message)

# --- Page: Business Insights ---
elif page == "Business Insights":
    st.title("📈 Business Insights")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Enrollment History", "Authentication Log", "De-duplication Log"])

    with tab1:
        st.header("Enrollment History")
        history_records = get_enrollment_history()
        history_df = pd.DataFrame(history_records, columns=["Aadhaar ID", "Name", "Date of Birth", "Gender", "Address", "Biometric ID", "Enrollment Date"])
        st.dataframe(history_df)

        st.subheader("Enrollments by Gender")
        enrollment_by_gender = history_df.groupby("Gender").size().reset_index(name="Count")
        st.bar_chart(enrollment_by_gender.set_index("Gender"))

    with tab2:
        st.header("Authentication Log")
        log_records = get_authentication_log()
        log_df = pd.DataFrame(log_records, columns=["Log ID", "Aadhaar ID", "Attempt Date", "Successful"])
        st.dataframe(log_df)

        st.subheader("Authentication Attempts Over Time")
        log_df['Date'] = log_df['Attempt Date'].dt.date
        auth_over_time = log_df.groupby('Date').size().reset_index(name='Total Attempts')
        st.line_chart(auth_over_time.set_index('Date'))
        
        st.subheader("Min/Max/Avg Attempts")
        min_attempts = auth_over_time['Total Attempts'].min()
        max_attempts = auth_over_time['Total Attempts'].max()
        avg_attempts = auth_over_time['Total Attempts'].mean()
        st.write(f"**Minimum Daily Attempts:** {min_attempts}")
        st.write(f"**Maximum Daily Attempts:** {max_attempts}")
        st.write(f"**Average Daily Attempts:** {avg_attempts:.2f}")

    with tab3:
        st.header("De-duplication Log")
        dedup_records = get_deduplication_log()
        dedup_df = pd.DataFrame(dedup_records, columns=["Log ID", "Biometric ID", "Conflict Date"])
        st.dataframe(dedup_df)
        st.write(f"**Total De-duplication Conflicts:** {len(dedup_df)}")