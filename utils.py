import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import pandas as pd
import os

def initialize_firestore():
    """
    Initialize Firestore with improved error handling and logging
    """
    if not firebase_admin._apps:
        cred = None
        
        # 1. Try Streamlit secrets (for production deployment)
        try:
            if hasattr(st, 'secrets') and 'firebase' in st.secrets:
                firebase_secrets = {
                    "type": st.secrets.firebase.type,
                    "project_id": st.secrets.firebase.project_id,
                    "private_key_id": st.secrets.firebase.private_key_id,
                    "private_key": st.secrets.firebase.private_key.replace('\\n', '\n'),
                    "client_email": st.secrets.firebase.client_email,
                    "client_id": st.secrets.firebase.client_id,
                    "auth_uri": st.secrets.firebase.auth_uri,
                    "token_uri": st.secrets.firebase.token_uri,
                    "auth_provider_x509_cert_url": st.secrets.firebase.auth_provider_x509_cert_url,
                    "client_x509_cert_url": st.secrets.firebase.client_x509_cert_url
                }
                cred = credentials.Certificate(firebase_secrets)
                print("Using Streamlit secrets for Firebase credentials")
        except Exception as e:
            print(f"Could not load Streamlit secrets: {e}")
        
        # 2. Try local credential file (development only)
        if cred is None:
            local_cred_path = "Credential/bro-salary-firebase-adminsdk-fbsvc-cf452594f8.json"
            if os.path.exists(local_cred_path):
                try:
                    cred = credentials.Certificate(local_cred_path)
                except Exception as e:
                    print(f"Local credential file error: {e}")
        
        # Initialize Firebase
        if cred:
            try:
                firebase_admin.initialize_app(cred)
            except Exception as e:
                st.error(f"Firebase initialization failed: {e}")
                return None
        else:
            st.error("⚠️ 無法初始化 Firebase。請檢查憑證配置。")
            return None
    
    try:
        return firestore.client()
    except Exception as e:
        st.error(f"⚠️ 無法連接到 Firestore: {e}")
        return None

def get_all_employees(db):
    """
    Fetch all employee data from Firestore Employee collection.

    Args:
        db: Firestore client instance

    Returns:
        pd.DataFrame: Employee data with columns [綽號, 全名, 月薪, 平均薪資]
    """
    if not db:
        return pd.DataFrame()
        
    nickname = []
    employee_name = []
    employee_salary = []
    employee_hourly_rate = []

    try:
        for i in db.collection("Employee").stream():
            nickname.append(i.id)
            employee_info = i.to_dict()
            employee_name.append(employee_info.get("Name", ""))
            employee_salary.append(employee_info.get("Salary", 0))
            employee_hourly_rate.append(employee_info.get("Hourly_Rate", 0))

        db_employee = pd.DataFrame({
            "綽號": nickname, 
            "全名": employee_name, 
            "月薪": employee_salary, 
            "平均薪資": employee_hourly_rate
        })
        
        return db_employee
    
    except Exception as e:
        error_msg = f"Error fetching employee data: {e}"
        if hasattr(st, 'error'):
            st.error(error_msg)
        print(error_msg)
        return pd.DataFrame()

def calculate_work_time(check_in, check_out):
    """
    Calculate work time between check-in and check-out timestamps.
    Handles overnight shifts automatically.
    
    Args:
        check_in: Check-in timestamp
        check_out: Check-out timestamp
        
    Returns:
        float: Work hours or pd.NaT if calculation fails
    """
    import datetime
    
    if pd.isna(check_in) or pd.isna(check_out):
        return pd.NaT
    
    # Ensure datetime objects
    if not isinstance(check_in, (pd.Timestamp, datetime.datetime)):
        try:
            check_in = pd.to_datetime(check_in)
        except:
            return pd.NaT
    
    if not isinstance(check_out, (pd.Timestamp, datetime.datetime)):
        try:
            check_out = pd.to_datetime(check_out)
        except:
            return pd.NaT
    
    # Handle overnight shifts
    if check_out < check_in:
        check_out = check_out + pd.Timedelta(days=1)
    
    return(check_out - check_in).total_seconds() / 3600

def format_time(hours):
    """
    Format hours as HH:MM string.
    
    Args:
        hours: Number of hours as float
        
    Returns:
        str: Formatted time string (HH:MM) or empty string if invalid
    """
    if pd.isna(hours):
        return ""
    
    total_minutes = int(hours * 60)
    hours_int = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours_int:02d}:{minutes:02d}"