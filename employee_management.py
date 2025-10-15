import streamlit as st
import pandas as pd
from datetime import datetime
from utils import initialize_firestore, get_all_employees


def display_employees(employee_df):
    """Display employee data in a Streamlit dataframe"""
    if employee_df.empty:
        st.info("資料庫中無任何資料。")
        return employee_df
    
    # Display the DataFrame
    st.dataframe(employee_df)
    
    # Return the DataFrame for further use
    return employee_df

def add_employee(db):
    """Form for adding a new employee"""
    st.subheader("新增員工")
    
    # Create form with required fields based on your data structure
    with st.form("add_employee_form"):
        # Basic info
        col1, col2, col3 = st.columns(3)
        with col1:
            nickname = st.text_input("員工綽號 (將作為資料庫 ID)")
            full_name = st.text_input("員工全名")
        
        with col2:
            salary = st.number_input("月薪", min_value=0.00, value=30000.00, step=1000.00)
        
        with col3:
            hourly_rate = st.number_input("平均薪資", min_value=0.00, value=166.67, step=0.01)
        
        # Additional info (optional)
        notes = st.text_area("備註")
        
        # Submit button
        submitted = st.form_submit_button("新增員工")
    
    if submitted:
        if not nickname or not full_name:
            st.error("員工綽號和全名為必填項")
            return
        
        # Create employee document based on your data structure
        employee_data = {
            "Name": full_name,
            "Salary": salary,
            "Hourly_Rate": hourly_rate,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add notes if provided
        if notes:
            employee_data["Notes"] = notes
        
        try:
            # Check if employee already exists
            doc_ref = db.collection("Employee").document(nickname)
            doc = doc_ref.get()
            
            if doc.exists:
                st.error(f"員工 '{nickname}' 已存在，請使用更新功能或使用其他綽號")
                return
            
            # Add employee to Firestore using the nickname as document name
            db.collection("Employee").document(nickname).set(employee_data)
            st.success(f"員工 '{full_name}' (綽號: {nickname}) 已成功新增，請刷新頁面")
            
            # Refresh the page to show updated data
            # st.experimental_rerun()
        
        except Exception as e:
            st.error(f"新增員工時發生錯誤: {str(e)}")

def update_employee(db, employee_df):
    """Form for updating an existing employee"""
    st.subheader("更新員工資料")
    
    if employee_df is None or employee_df.empty:
        st.warning("沒有員工資料可更新")
        return
    
    # Get list of employee nicknames for selection
    employee_nicknames = employee_df['綽號'].tolist()
    selected_employee = st.selectbox("選擇要更新的員工", employee_nicknames)
    
    # Get current employee data
    selected_row = employee_df[employee_df['綽號'] == selected_employee].iloc[0]
    
    # Create update form
    with st.form("update_employee_form"):
        # Allow updating name and salary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            updated_name = st.text_input("全名", value=selected_row['全名'])
        
        with col2:
            updated_salary = st.number_input(
                "月薪", 
                value=float(selected_row['月薪']), 
                min_value=0.0, 
                step=1000.0
            )

        with col3:
            calculated_hourly_rate = round(updated_salary / 30 / 8, 2)
            st.caption(f"自動計算: {updated_salary:,.0f} ÷ 30 ÷ 8 = {calculated_hourly_rate:.2f}")


            updated_hourly_rate = st.number_input(
                "平均薪資", 
                value=float(selected_row['平均薪資']), 
                min_value=0.0, 
                step=1000.0,
                help="預設為月薪÷30天÷8小時，可手動調整"
            )
        
        # Additional fields (optional)
        notes = st.text_area("備註")
        
        # Build the update data dictionary
        updated_data = {
            "Name": updated_name,
            "Salary": updated_salary,
            "Hourly_Rate": updated_hourly_rate
        }
        
        # Add notes if provided
        if notes:
            updated_data["Notes"] = notes
            
        # Add update timestamp
        updated_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Submit button
        submitted = st.form_submit_button("更新員工資料")
    
    if submitted:
        try:
            # Check if anything changed
            if (updated_name != selected_row['全名'] or 
                updated_salary != selected_row['月薪'] or 
                updated_hourly_rate != selected_row['平均薪資'] or 
                notes):
                # Update employee in Firestore
                db.collection("Employee").document(selected_employee).update(updated_data)
                st.success(f"員工 '{selected_employee}' 資料已成功更新，請刷新頁面")
                
                # Refresh the page to show updated data
                # st.experimental_rerun()
            else:
                st.info("沒有資料被更改")
        
        except Exception as e:
            st.error(f"更新員工資料時發生錯誤: {str(e)}")

def delete_employee(db, employee_df):
    """Form for deleting an existing employee"""
    st.subheader("刪除員工")
    
    if employee_df is None or employee_df.empty:
        st.warning("沒有員工資料可刪除")
        return
    
    # Get list of employee nicknames for selection
    employee_nicknames = employee_df['綽號'].tolist()
    selected_employee = st.selectbox("選擇要刪除的員工", employee_nicknames, key="delete_select")
    
    # Show employee details before deletion
    if selected_employee:
        selected_row = employee_df[employee_df['綽號'] == selected_employee].iloc[0]
        
        # Display important employee info
        st.write(f"員工綽號: {selected_employee}")
        st.write(f"員工全名: {selected_row['全名']}")
        st.write(f"員工月薪: {selected_row['月薪']}")
        st.write(f"員工月薪: {selected_row['平均薪資']}")
        
        # Confirmation checkbox
        confirm = st.checkbox("我確認要刪除此員工資料 (此操作無法復原)")
        
        if confirm:
            delete_button = st.button("刪除員工")
            
            if delete_button:
                try:
                    # Delete employee from Firestore
                    db.collection("Employee").document(selected_employee).delete()
                    st.success(f"員工 '{selected_employee}' 已成功刪除，請刷新頁面")
                    
                    # Refresh the page to show updated data
                    # st.experimental_rerun()
                
                except Exception as e:
                    st.error(f"刪除員工時發生錯誤: {str(e)}")

def run_employee_management():
    """Main function to run the employee management page"""
    st.title("員工管理")
    
    # Initialize Firestore
    db = initialize_firestore()
    
    if not db:
        st.error("無法連接到資料庫。請檢查您的 Firebase 憑證。")
        return
    
    # Fetch and display employee data
    st.subheader("員工資料")
    employee_df = get_all_employees(db)
    display_employees(employee_df)
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["新增員工", "更新員工資料", "刪除員工"])
    
    with tab1:
        add_employee(db)
    
    with tab2:
        update_employee(db, employee_df)
    
    with tab3:
        delete_employee(db, employee_df)

if __name__ == "__main__":
    run_employee_management()