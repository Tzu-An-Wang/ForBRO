import streamlit as st
import hashlib
from datetime import datetime
from utils import initialize_firestore
import time


def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(db, username, password, role="user"):
    """Create a new user in Firestore - simplified to admin/user roles"""
    try:
        # Ensure role is either 'admin' or 'user'
        if role not in ["admin", "user"]:
            role = "user"
            
        hashed_password = hash_password(password)
        user_data = {
            "username": username,
            "password_hash": hashed_password,
            "role": role,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "active": True
        }
        
        db.collection("Users").document(username).set(user_data)
        return True
    except Exception as e:
        st.error(f"創建使用者失敗: {e}")
        return False

def verify_user(db, username, password):
    """Verify user credentials against Firestore"""
    try:
        doc_ref = db.collection("Users").document(username)
        doc = doc_ref.get()
        
        if doc.exists:
            user_data = doc.to_dict()
            if user_data.get("active", False):
                stored_hash = user_data.get("password_hash")
                return stored_hash == hash_password(password)
        return False
    except Exception as e:
        st.error(f"驗證失敗: {e}")
        return False
    
def get_wheat_code():
    """Get wheat code from secrets"""
    return st.secrets.get("wheat_code")

def verify_wheat_code(wheat_input):
    """Verify the wheat security code"""
    return wheat_input == get_wheat_code()

def get_user_role(db, username):
    """Get user role from Firestore"""
    try:
        doc_ref = db.collection("Users").document(username)
        doc = doc_ref.get()
        
        if doc.exists:
            user_data = doc.to_dict()
            return user_data.get("role", "user")
        return None
    except Exception as e:
        st.error(f"獲取使用者角色失敗: {e}")
        return None

def change_password(db, username, current_password, new_password, wheat_code):
    """Change user password with verification"""
    try:
        # Verify wheat code first
        if not verify_wheat_code(wheat_code):
            return False, "安全碼錯誤"
        
        # Verify current password
        if not verify_user(db, username, current_password):
            return False, "當前密碼錯誤"
        
        # Update password
        new_hash = hash_password(new_password)
        update_data = {
            "password_hash": new_hash,
            "password_changed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        db.collection("Users").document(username).update(update_data)
        return True, "密碼更改成功"
        
    except Exception as e:
        return False, f"更改密碼時發生錯誤: {str(e)}"

def show_password_change_form():
    """Display password change form for current user"""
    st.subheader("🔑 更改密碼")
    
    current_user = get_current_user()
    if not current_user:
        st.error("請先登入")
        return
    
    db = initialize_firestore()
    if not db:
        st.error("無法連接到資料庫")
        return
    
    with st.form("change_password_form"):
        st.write(f"更改使用者 '{current_user}' 的密碼")
        
        current_password = st.text_input("當前密碼", type="password", placeholder="請輸入您的當前密碼")
        new_password = st.text_input("新密碼", type="password", placeholder="請輸入新密碼")
        confirm_password = st.text_input("確認新密碼", type="password", placeholder="請再次輸入新密碼")
        wheat_code = st.text_input("安全碼", type="password", placeholder="請輸入系統安全碼", help="請輸入系統安全碼進行驗證")
        
        submitted = st.form_submit_button("🔄 更改密碼", type="primary")
        
        if submitted:
            # Validation
            if not current_password or not new_password or not confirm_password or not wheat_code:
                st.error("⚠️ 請填寫所有欄位")
                return
            
            if new_password != confirm_password:
                st.error("❌ 新密碼和確認密碼不一致")
                return
            
            if len(new_password) < 6:
                st.error("❌ 新密碼至少需要6個字符")
                return
            
            if new_password == current_password:
                st.warning("⚠️ 新密碼不能與當前密碼相同")
                return
            
            # Change password
            success, message = change_password(db, current_user, current_password, new_password, wheat_code)
            
            if success:
                st.success(f"✅ {message}")
                st.info("🔄 密碼已更改，請使用新密碼重新登入")
                st.balloons()  # Celebration effect
                
                # Auto logout after 3 seconds

                with st.spinner("3秒後自動登出..."):
                    time.sleep(3)
                logout()
            else:
                st.error(f"❌ {message}")

def login_form():
    """Display login form with Firestore authentication and wheat code"""
    st.title("🔐 員工管理系統登入")
    
    # Initialize Firestore
    db = initialize_firestore()
    if not db:
        st.error("無法連接到資料庫")
        return
    
    with st.form("login_form"):
        st.subheader("請輸入登入資訊")
        
        # Three input fields as requested
        username = st.text_input("使用者名稱", placeholder="請輸入您的使用者名稱")
        password = st.text_input("密碼", type="password", placeholder="請輸入您的密碼")
        wheat = st.text_input("安全碼", type="password", placeholder="請輸入安全碼", help="請輸入系統安全碼")
        
        # Single login button
        login_submitted = st.form_submit_button("🔑 登入", type="primary")
        
        if login_submitted:
            # Check if all fields are filled
            if not username or not password or not wheat:
                st.warning("⚠️ 請填寫所有必填欄位")
                return
            
            # First verify wheat code
            if not verify_wheat_code(wheat):
                st.error("❌ 安全碼錯誤")
                return
            
            # Then verify user credentials
            if verify_user(db, username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_role = get_user_role(db, username)
                st.success("✅ 登入成功!")
                st.rerun()
            else:
                st.error("❌ 使用者名稱或密碼錯誤")
    
    # Simple info for users
    st.divider()
    st.info("💡 需要帳號請聯繫系統管理員")

def show_all_users(db):
    """Show all users for admin (only if admin is logged in)"""
    if st.session_state.get("user_role") != "admin":
        st.error("❌ 需要管理員權限")
        return
    
    try:
        st.subheader("👥 系統使用者列表")
        
        users = []
        for doc in db.collection("Users").stream():
            user_data = doc.to_dict()
            users.append({
                "使用者名稱": doc.id,
                "角色": user_data.get("role", "user"),
                "狀態": "啟用" if user_data.get("active", False) else "停用",
                "創建時間": user_data.get("created_at", "未知"),
                "最後密碼更改": user_data.get("password_changed_at", "未更改過")
            })
        
        if users:
            import pandas as pd
            df = pd.DataFrame(users)
            st.dataframe(df, use_container_width=True)
            
            # Show summary
            total_users = len(users)
            admin_count = len([u for u in users if u["角色"] == "admin"])
            user_count = len([u for u in users if u["角色"] == "user"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("總使用者數", total_users)
            with col2:
                st.metric("管理員", admin_count)
            with col3:
                st.metric("一般使用者", user_count)
        else:
            st.info("💡 系統中沒有使用者")
            
    except Exception as e:
        st.error(f"獲取使用者列表失敗: {e}")

def logout():
    """Logout function"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.show_create_user = False
    st.session_state.show_users = False
    st.session_state.show_change_password = False
    st.rerun()

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get("logged_in", False)

def get_current_user():
    """Get current logged in user"""
    return st.session_state.get("username", None)

def get_user_role_session():
    """Get current user's role"""
    return st.session_state.get("user_role", "user")

def require_auth(func):
    """Decorator to require authentication for functions"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            login_form()
            return
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin role"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            login_form()
            return
        
        if get_user_role_session() != "admin":
            st.error("❌ 需要管理員權限才能訪問此功能")
            return
        
        return func(*args, **kwargs)
    return wrapper

# Helper function to create initial admin user
def create_initial_admin():
    """Create initial admin user - run this once to set up the system"""
    db = initialize_firestore()
    if not db:
        print("無法連接到資料庫")
        return False
    
    # Check if admin already exists
    admin_doc = db.collection("Users").document("admin").get()
    if admin_doc.exists:
        print("管理員使用者已存在")
        return True
    
    # Create admin user
    admin_data = {
        "username": "admin",
        "password_hash": hash_password("admin123"),  # Change this password!
        "role": "admin",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active": True
    }
    
    try:
        db.collection("Users").document("admin").set(admin_data)
        print("管理員使用者創建成功!")
        print("使用者名稱: admin")
        print("密碼: admin123")
        print("安全碼: wheat")
        print("請在首次登入後更改密碼!")
        return True
    except Exception as e:
        print(f"創建管理員失敗: {e}")
        return False

if __name__ == "__main__":
    # Run this to create initial admin user
    create_initial_admin()