# app.py
import streamlit as st
from pos_converter import run_pos_converter
from payroll_calculator import run_salary_calculator
from employee_management import run_employee_management
from firestore_auth import (login_form, logout, is_authenticated, 
                           get_current_user, get_user_role_session,
                           show_all_users, create_user, verify_wheat_code,
                           show_password_change_form)
from utils import initialize_firestore

def main():
    """Main application entry point with authentication and password change"""
    
    # Configure page
    st.set_page_config(
        page_title="員工管理系統",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # Check if user is authenticated
    if not is_authenticated():
        login_form()
        return
    
    # User is authenticated, show the main app
    current_user = get_current_user()
    user_role = get_user_role_session()
    
    # Sidebar header
    st.sidebar.title("🏢 員工管理系統")
    st.sidebar.divider()
    
    # User info section
    st.sidebar.subheader("使用者資訊")
    st.sidebar.write(f"👤 **使用者**: {current_user}")
    
    # Role display - simplified to admin/others
    if user_role == "admin":
        st.sidebar.write("👑 **角色**: 管理員")
    else:
        st.sidebar.write("👤 **角色**: 一般使用者")
    
    if st.sidebar.button("🚪 登出", type="secondary"):
        logout()
    
    st.sidebar.divider()
    
    # Options for the sidebar - all users have access to all business functions
    options = [
        "POS 轉 Excel", 
        "員工工時計算", 
        "員工管理"
    ]
    
    st.sidebar.subheader("功能選擇")
    selected_function = st.sidebar.radio("選擇功能:", options)
    
    # Show admin-only features in sidebar
    if user_role == "admin":
        st.sidebar.divider()
        st.sidebar.subheader("🔧 管理員專用")
        st.sidebar.caption("🔒 三層驗證已啟用")
        st.sidebar.caption("🛡️ Firestore 認證")
        
        # Admin can access user management through sidebar
        if st.sidebar.button("👥 查看所有使用者"):
            st.session_state.show_users = True
            st.session_state.show_create_user = False
            st.session_state.show_change_password = False
            st.rerun()
        
        if st.sidebar.button("➕ 創建新使用者"):
            st.session_state.show_create_user = True
            st.session_state.show_users = False
            st.session_state.show_change_password = False
            st.rerun()
    
    # Password change option for all users
    st.sidebar.divider()
    st.sidebar.subheader("🔑 帳戶設定")
    if st.sidebar.button("🔑 更改密碼"):
        st.session_state.show_change_password = True
        st.session_state.show_users = False
        st.session_state.show_create_user = False
        st.rerun()
    
    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Welcome message
        st.title(f"歡迎回來, {current_user}! 👋")
        
        # Role-specific welcome message
        if user_role == "admin":
            st.success("🎉 管理員權限 - 可訪問所有功能及使用者管理")
        else:
            st.info("📊 一般使用者 - 可訪問所有業務功能")
    
    # Add spacing
    st.write("")
    st.write("")
    
    # Show user management if admin requested it
    if user_role == "admin" and st.session_state.get("show_users", False):
        st.subheader("👥 使用者管理")
        
        # Close button
        if st.button("❌ 關閉使用者管理"):
            st.session_state.show_users = False
            st.rerun()
        
        # Show users using imported function
        db = initialize_firestore()
        if db:
            show_all_users(db)
        
        return  # Don't show other functions when showing user management
    
    # Show create user form if admin requested it
    if user_role == "admin" and st.session_state.get("show_create_user", False):
        st.subheader("➕ 創建新使用者")
        
        # Close button
        if st.button("❌ 關閉創建使用者"):
            st.session_state.show_create_user = False
            st.rerun()
        
        # Show create user form using imported functions
        db = initialize_firestore()
        if db:
            with st.form("admin_create_user_form"):
                st.write("管理員創建新使用者")
                
                new_username = st.text_input("新使用者名稱", placeholder="請輸入使用者名稱")
                new_password = st.text_input("新使用者密碼", type="password", placeholder="請輸入使用者密碼")
                new_role = st.selectbox("使用者角色", ["user", "admin"], help="選擇使用者的系統角色")
                wheat_verify = st.text_input("管理員安全碼確認", type="password", placeholder="請輸入安全碼")
                
                if st.form_submit_button("✅ 創建使用者", type="primary"):
                    if new_username and new_password and wheat_verify:
                        if verify_wheat_code(wheat_verify):
                            if create_user(db, new_username, new_password, new_role):
                                st.success(f"✅ 使用者 '{new_username}' 創建成功!")
                                st.info(f"角色: {new_role}")
                                st.balloons()
                            else:
                                st.error("❌ 使用者創建失敗")
                        else:
                            st.error("❌ 管理員安全碼錯誤")
                    else:
                        st.warning("⚠️ 請填寫所有欄位")
        
        return  # Don't show other functions when showing create user
    
    # Show password change form if requested
    if st.session_state.get("show_change_password", False):
        # Close button
        if st.button("❌ 關閉更改密碼"):
            st.session_state.show_change_password = False
            st.rerun()
        
        # Show password change form
        show_password_change_form()
        return  # Don't show other functions when changing password
    
    # Run the selected function - all users have access to all business functions
    try:
        if selected_function == "POS 轉 Excel":
            run_pos_converter()
        elif selected_function == "員工工時計算":
            run_salary_calculator()  # This calls your payroll calculator
        elif selected_function == "員工管理":
            run_employee_management()  # All users can access this
    
    except Exception as e:
        st.error(f"❌ 運行功能時發生錯誤: {e}")
        st.info("🔧 請聯繫系統管理員檢查系統狀態")

if __name__ == "__main__":
    main()