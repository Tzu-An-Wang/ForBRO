import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime
from io import BytesIO
from utils import initialize_firestore, get_all_employees


def separate_employee_records(df, df_salary):
    """
    Separate employee records and calculate overtime payments
    
    Parameters:
    df: DataFrame containing the time records(Time_Record.xlsx)
    df_salary: DataFrame containing employee salary information with columns ['綽號', '平均薪資'] from firestore
    
    Returns:
    dict: Dictionary with employee names as keys and their work records as DataFrames
    """
    
    # Get all employee names
    names = [i for i in df["小麥過敏"] if i not in ["上班", "下班", np.nan] and "總時數" not in str(i)]
    
    # Find all "總時數" rows once (outside the loop)
    total_hours_mask = df["小麥過敏"].astype(str).str.contains("總時數")
    total_hours_indices = df[total_hours_mask].index
    
    # Dictionary to store each employee's records
    employee_records = {}
    
    # Error handling for salary data
    try:
        employee_salary = df_salary.set_index('綽號')['月薪'].to_dict()
        employee_hourly_rate = df_salary.set_index('綽號')['平均薪資'].to_dict()
    except KeyError as e:
        st.error(f"Error: Required column not found in salary data: {e}")
        return {}
    except Exception as e:
        st.error(f"Error processing salary data: {e}")
        return {}

    for name in names:
        # Check if employee exists in salary data
        if name not in employee_salary or name not in employee_hourly_rate:
            st.warning(f"Employee '{name}' not found in salary data. Skipping...")
            continue
            
        try:
            # Find the row index where this name appears
            name_index = df[df["小麥過敏"] == name].index[0]
        except IndexError:
            st.warning(f"Employee '{name}' not found in time records. Skipping...")
            continue
        
        # Find the first "總時數" row that comes after the name
        end_index = None
        for idx in total_hours_indices:
            if idx > name_index:
                end_index = idx
                break
        
        # Extract all rows between name and "總時數" (or end of dataframe)
        if end_index is not None:
            raw_data = df.loc[name_index:end_index]
        else:
            raw_data = df.loc[name_index:]
        
        # Filter only the clock-in and clock-out rows
        clock_rows = raw_data[raw_data["小麥過敏"].isin(["上班", "下班"])]
        
        salary = employee_salary[name]
        hourly_rate = employee_hourly_rate[name]
        
        # Validate salary data
        if not isinstance(salary, (int, float)) or salary <= 0:
            st.warning(f"Invalid salary for '{name}': {salary}. Using 0.")
            salary = 0
        if not isinstance(hourly_rate, (int, float)) or hourly_rate <= 0:
            st.warning(f"Invalid hourly rate for '{name}': {hourly_rate}. Using 0.")
            hourly_rate = 0

        # Prepare lists for the new dataframe
        dates = []
        clock_ins = []
        clock_outs = []
        work_hours = []
        work_hours_formatted = []  
        hours_8_10 = []
        hours_10_12 = []
        overtime_payment_8_10 = [] 
        overtime_payment_10_12 = [] 
        salary_column = []
        hourly_rate_column = []
        
        # Process in pairs (上班/下班)
        i = 0
        while i < len(clock_rows) - 1:
            if clock_rows.iloc[i]["小麥過敏"] == "上班" and clock_rows.iloc[i+1]["小麥過敏"] == "下班":
                # Extract clock-in time details
                timestamp_column = clock_rows.columns[1]
                
                # Get timestamps
                clock_in_str = str(clock_rows.iloc[i][timestamp_column])
                clock_out_str = str(clock_rows.iloc[i+1][timestamp_column])
                
                try:
                    # Try to parse the date from clock-in timestamp
                    if "-" in clock_in_str:
                        date_format = "%Y-%m-%d"
                        time_format = "%H:%M:%S"
                    else:
                        date_format = "%Y/%m/%d"
                        time_format = "%H:%M"
                    
                    # Extract date and times
                    date_part = clock_in_str.split()[0]
                    clock_in_time = clock_in_str.split()[1] if len(clock_in_str.split()) > 1 else clock_in_str
                    clock_out_time = clock_out_str.split()[1] if len(clock_out_str.split()) > 1 else clock_out_str
                    
                    try:
                        # Parse the time strings
                        clock_in_dt = datetime.strptime(date_part + " " + clock_in_time, date_format + " " + time_format)
                        clock_out_dt = datetime.strptime(date_part + " " + clock_out_time, date_format + " " + time_format)
                        
                        # Check for overnight shifts (should not exist)
                        if clock_out_dt < clock_in_dt:
                            error_msg = (f"OVERNIGHT SHIFT DETECTED for employee '{name}' on {date_part}:\n"
                                       f"Clock-in: {clock_in_time}\n"
                                       f"Clock-out: {clock_out_time}\n"
                                       f"This indicates a data error as overnight shifts should not exist.")
                            st.error(error_msg)
                            continue
                        
                        # Calculate work duration in hours
                        work_duration_seconds = (clock_out_dt - clock_in_dt).total_seconds()
                        work_duration_hours = work_duration_seconds / 3600

                        if work_duration_hours < 0 or work_duration_hours > 24:
                            st.warning(f"Unusual work duration for {name} on {date_part}: {work_duration_hours:.2f} hours")
                        
                        # Format work duration as hours and minutes
                        hours = int(work_duration_hours)
                        minutes = int((work_duration_hours - hours) * 60)
                        work_duration_formatted = f"{hours} hours {minutes} min"
                        
                        # Calculate hours in 8-10 hour interval
                        hours_in_8_10 = 0
                        if work_duration_hours > 8:
                            if work_duration_hours >= 10:
                                hours_in_8_10 = 2
                            else:
                                hours_in_8_10 = work_duration_hours - 8
                                
                            # Round to nearest 0.2 hours (12 minutes)
                            minutes_fraction = (hours_in_8_10 * 60) % 60
                            hours_in_8_10 = int(hours_in_8_10) + (math.ceil(minutes_fraction / 12) * 0.2)
                        
                        # Calculate hours in 10-12 hour interval
                        hours_in_10_12 = 0
                        if work_duration_hours > 10:
                            hours_in_10_12 = work_duration_hours - 10
                                
                            # Round to nearest 0.2 hours (12 minutes)
                            minutes_fraction = (hours_in_10_12 * 60) % 60
                            hours_in_10_12 = int(hours_in_10_12) + (math.ceil(minutes_fraction / 12) * 0.2)

                        payment_8_10 = hours_in_8_10 * hourly_rate * 1.33
                        payment_10_12 = hours_in_10_12 * hourly_rate * 1.67
                        
                        # Add to our records
                        dates.append(date_part)
                        clock_ins.append(clock_in_time)
                        clock_outs.append(clock_out_time)
                        work_hours.append(f"{work_duration_hours:.2f}")
                        work_hours_formatted.append(work_duration_formatted)
                        hours_8_10.append(f"{hours_in_8_10:.1f}")
                        hours_10_12.append(f"{hours_in_10_12:.1f}")
                        overtime_payment_8_10.append(f"{payment_8_10:.2f}")
                        overtime_payment_10_12.append(f"{payment_10_12:.2f}")

                        if len(dates) == 1:  # First row
                            salary_column.append(f"{salary:,.0f}")
                            hourly_rate_column.append(f"{hourly_rate:.2f}")
                        else:  # Subsequent rows
                            salary_column.append("")
                            hourly_rate_column.append("")
                        
                    except (ValueError, TypeError) as e:
                        st.warning(f"Time parsing failed for {name} on {date_part}: {e}")
                        # If time parsing fails, record strings without calculating hours
                        dates.append(date_part)
                        clock_ins.append(clock_in_time)
                        clock_outs.append(clock_out_time)
                        work_hours.append("N/A")
                        work_hours_formatted.append("N/A")
                        hours_8_10.append("N/A")
                        hours_10_12.append("N/A")
                        overtime_payment_8_10.append("N/A")
                        overtime_payment_10_12.append("N/A")
                                                
                        if len(dates) == 1:  # First row
                            salary_column.append(f"{salary:,.0f}")
                            hourly_rate_column.append(f"{hourly_rate:.2f}")
                        else:  # Subsequent rows
                            salary_column.append("")
                            hourly_rate_column.append("")
                        
                except (ValueError, TypeError, IndexError) as e:
                    st.warning(f"Date parsing failed for {name}: {e}")
                    # If date parsing fails, use raw strings
                    dates.append("N/A")
                    clock_ins.append(clock_in_str)
                    clock_outs.append(clock_out_str)
                    work_hours.append("N/A")
                    work_hours_formatted.append("N/A")
                    hours_8_10.append("N/A")
                    hours_10_12.append("N/A")
                    overtime_payment_8_10.append("N/A")
                    overtime_payment_10_12.append("N/A")

                    if len(dates) == 1:  # First row
                        salary_column.append(f"{salary:,.0f}")
                        hourly_rate_column.append(f"{hourly_rate:.2f}")
                    else:  # Subsequent rows
                        salary_column.append("")
                        hourly_rate_column.append("")
                
                i += 2  # Move to the next pair
            else:
                i += 1  # Skip unpaired records
        
        # Only create DataFrame if we have data
        if dates:
            # Create the formatted dataframe
            employee_df = pd.DataFrame({
                "日期": dates,
                "上班": clock_ins,
                "下班": clock_outs,
                "工作時數(小時)": work_hours,
                "工作時間": work_hours_formatted,
                "8-10小時區間": hours_8_10,
                "10-12小時區間": hours_10_12,
                "8-10小時加班費": overtime_payment_8_10,
                "10-12小時加班費": overtime_payment_10_12,
                "工資": salary_column,  
                "平均薪資": hourly_rate_column  
            })
            
            employee_records[name] = employee_df
        else:
            st.warning(f"No valid time records found for employee '{name}'")
    
    return employee_records

def export_all_employees_to_excel(employee_records):
    """
    Export all employee records to a single Excel file with multiple sheets
    
    Parameters:
    employee_records: Dictionary with employee names as keys and DataFrames as values
    
    Returns:
    BytesIO: Excel file buffer for download
    """
    if not employee_records:
        st.error("No employee records to export")
        return None
    
    try:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Create a summary sheet
            summary_data = []
            for name, df in employee_records.items():
                if not df.empty:
                    # Calculate totals for each employee
                    total_work_hours = 0
                    total_8_10_payment = 0
                    total_10_12_payment = 0
                    
                    for _, row in df.iterrows():
                        if row['工作時數(小時)'] != "N/A" and row['工作時數(小時)'] != "":
                            try:
                                total_work_hours += float(row['工作時數(小時)'])
                            except (ValueError, TypeError):
                                pass
                        
                        if row['8-10小時加班費'] != "N/A" and row['8-10小時加班費'] != "":
                            try:
                                total_8_10_payment += float(row['8-10小時加班費'])
                            except (ValueError, TypeError):
                                pass
                        
                        if row['10-12小時加班費'] != "N/A" and row['10-12小時加班費'] != "":
                            try:
                                total_10_12_payment += float(row['10-12小時加班費'])
                            except (ValueError, TypeError):
                                pass
                    
                    # Get salary info from first row
                    monthly_salary = df.iloc[0]['工資'] if not df.empty else ""
                    hourly_rate = df.iloc[0]['平均薪資'] if not df.empty else ""
                    
                    summary_data.append({
                        '員工綽號': name,
                        '月薪': monthly_salary,
                        '時薪': hourly_rate,
                        '總工時': f"{total_work_hours:.2f}",
                        '8-10小時加班費總計': f"{total_8_10_payment:.2f}",
                        '10-12小時加班費總計': f"{total_10_12_payment:.2f}",
                        '總加班費': f"{total_8_10_payment + total_10_12_payment:.2f}"
                    })
            
            # Write summary sheet
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='薪資摘要', index=False)
            
            # Write individual employee sheets
            for name, df in employee_records.items():
                if not df.empty:
                    # Clean sheet name (Excel has restrictions on sheet names)
                    sheet_name = name[:31]  # Excel sheet name limit is 31 characters
                    # Remove invalid characters
                    invalid_chars = ['/', '\\', '?', '*', '[', ']', ':']
                    for char in invalid_chars:
                        sheet_name = sheet_name.replace(char, '_')
                    
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return buffer
    
    except Exception as e:
        st.error(f"Error creating Excel file: {e}")
        return None

def run_salary_calculator():
    """Main function to run the salary calculator page"""
    st.title('員工薪資計算器')
    
    # Initialize Firestore and get employee data
    try:
        db = initialize_firestore()
        df_salary = get_all_employees(db)
        
        if df_salary.empty:
            st.error("無法從資料庫獲取員工資料。請確認資料庫連接和員工資料。")
            return
        
        # Display current employees
        st.subheader('目前員工資料')
        st.dataframe(df_salary)
        
    except Exception as e:
        st.error(f"資料庫連接失敗: {e}")
        return
    
    # File upload for time records
    st.subheader('上傳打卡記錄')
    uploaded_file = st.file_uploader('請上傳打卡記錄 Excel 檔案', type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Read the time records file
            df_time = pd.read_excel(uploaded_file)
            
            # Show preview of uploaded data
            st.subheader('打卡記錄預覽')
            st.dataframe(df_time.head())
            
            # Process button
            if st.button('處理薪資計算'):
                with st.spinner('正在處理薪資計算...'):
                    # Calculate salary records
                    employee_records = separate_employee_records(df_time, df_salary)
                    
                    if employee_records:
                        st.success(f"成功處理 {len(employee_records)} 位員工的薪資記錄")
                        
                        # Display results in tabs
                        if employee_records:
                            employee_names = list(employee_records.keys())
                            tabs = st.tabs(['摘要'] + employee_names)
                            
                            # Summary tab
                            with tabs[0]:
                                st.subheader('薪資計算摘要')
                                
                                for name, df in employee_records.items():
                                    if not df.empty:
                                        col1, col2, col3 = st.columns(3)
                                        
                                        with col1:
                                            st.metric(f"{name} - 總工作天數", f"{len(df)} 天")
                                        
                                        # Calculate total overtime payments
                                        total_8_10 = sum([float(x) for x in df['8-10小時加班費'] if x not in ['N/A', '']])
                                        total_10_12 = sum([float(x) for x in df['10-12小時加班費'] if x not in ['N/A', '']])
                                        
                                        with col2:
                                            st.metric(f"{name} - 8-10小時加班費", f"${total_8_10:.2f}")
                                        
                                        with col3:
                                            st.metric(f"{name} - 10-12小時加班費", f"${total_10_12:.2f}")
                                        
                                        st.divider()
                            
                            # Individual employee tabs
                            for i, (name, df) in enumerate(employee_records.items()):
                                with tabs[i+1]:
                                    st.subheader(f'{name} 的詳細薪資記錄')
                                    st.dataframe(df)
                        
                        # Export all data
                        st.subheader('匯出薪資報表')
                        excel_buffer = export_all_employees_to_excel(employee_records)
                        
                        if excel_buffer:
                            st.download_button(
                                label="下載完整薪資報表 (Excel)",
                                data=excel_buffer.getvalue(),
                                file_name=f"員工薪資報表_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                mime="application/vnd.ms-excel"
                            )
                    else:
                        st.error("無法處理薪資資料。請檢查上傳的檔案格式和員工資料。")
        
        except Exception as e:
            st.error(f"處理檔案時發生錯誤: {e}")

if __name__ == "__main__":
    run_salary_calculator()