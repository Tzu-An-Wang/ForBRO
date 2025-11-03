import streamlit as st


def show_tutorial():
    """Display tutorial page for the employee management system"""
    
    st.title("📚 系統使用教學")
    st.divider()
    
    # Overview section
    st.header("🎯 功能介紹")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **📊 POS 轉 Excel**
        
        將POS機中營業額資料轉成會計師指定格式
        """)
    
    with col2:
        st.info("""
        **👥 員工管理**
        
        新增/變更/刪除/紀錄員工月薪及平均薪資
        """)
    
    with col3:
        st.info("""
        **⏰ 員工工時計算**
        
        計算並下載員工加班費
        """)
    
    st.divider()
    
    # Usage instructions
    st.header("📖 使用說明")
    
    # Workflow
    st.subheader("🔄 使用流程")
    st.success("POS 轉 Excel → 員工管理 → 員工工時計算")
    
    st.divider()
    
    # ==== POS Converter Tutorial ====
    st.subheader("1️⃣ POS 轉 Excel")
    
    with st.expander("📋 查看詳細說明", expanded=True):
        st.markdown("""
        ### 操作步驟：
        
        1. 將本月營收資料拖曳至上傳格子內
        2. 系統會自動生成會計師指定格式資料
        3. 確認預覽資料無誤後點選 **"點此下載"** 下載檔案
        """)
        
        st.info("💡 **提示**：系統會自動處理日期格式和累積營收計算")
    
    st.divider()
    
    # ==== Employee Management Tutorial ====
    st.subheader("2️⃣ 員工管理")
    
    with st.expander("📋 查看詳細說明", expanded=True):
        
        # Step 1: Check employee data
        st.markdown("### 📝 步驟 1：確認員工資料")
        st.markdown("""
        確認員工月薪及平均薪資是否有誤
        
        ⚠️ **注意**：綽號需與打卡記錄中名字一致
        """)
        
        # Placeholder for Picture1
        st.image("tutorial_images/picture1_employee_list.png", 
                caption="圖1：員工資料預覽")
        
        st.divider()
        
        # Step 2: Update employee data
        st.markdown("### ✏️ 步驟 2：更新員工資料（如有需要）")
        st.markdown("""
        1. 如員工資料有誤，請點選 **"更新員工資料"** 標籤
        2. 選擇需要更新的員工
        3. 修改資料後點擊 **"更新員工資料"** 按鈕
        """)
        
        # Placeholder for Picture2
        st.image("tutorial_images/picture2_update_employee.png", 
                caption="圖2：更新員工資料介面")
        
        st.divider()
        
        # Step 3: Delete employee (optional)
        st.markdown("### 🗑️ 步驟 3：刪除員工資料（選用）")
        st.markdown("""
        1. 點選 **"刪除員工"** 標籤
        2. 選擇需要刪除的員工
        3. 勾選確認框後點擊 **"刪除員工"** 按鈕
        """)
        
        st.warning("💡 **個人建議**：即使員工離職也不要刪除員工資料，以便保留歷史記錄")
        
        # Placeholder for Picture3
        st.image("tutorial_images/picture3_delete_employee.png", 
                caption="圖3：刪除員工介面")
    
    st.divider()
    
    # ==== Payroll Calculator Tutorial ====
    st.subheader("3️⃣ 員工工時計算")
    
    with st.expander("📋 查看詳細說明", expanded=True):
        
        # Step 1: Check time records
        st.markdown("### 🔍 步驟 1：確認員工工時資料完整性")
        
        st.markdown("""
        **重要檢查項目：**

        ✅ 人名（王小明）需與”員工資料“裡“綽號”相同        
        ✅ 所有 **"上班"** 皆有 **"下班"** 配對
            如果只有上班或只有下班，請自行插入一列後輸入資料（如下圖，原本無上班資料，黃色為自行加上部分）
        """)
        
        st.info("""
        **📝 資料格式說明：**
        
        - 格式：`yyyy-MM-dd HH:mm:ss`
        - 範例：`2025-04-25 09:46:27`
        - Excel 上看起來不一樣沒關係（如下圖黃色部份），輸入正確即可
        """)
        
        # Placeholder for Picture4
        st.image("tutorial_images/picture4_time_record_fix.png", 
                caption="圖4：補充打卡資料範例（黃色為手動新增部分）")
        
        st.divider()
        
        # Step 2: Upload and process
        st.markdown("### 📤 步驟 2：上傳並處理資料")
        st.markdown("""
        1. 確認資料正確後，將員工工時資料拖曳至“上傳打卡記錄”格子內
        2. 點擊 **"處理薪資計算"** 按鈕
        """)
        
        # Placeholder for Picture5
        st.image("tutorial_images/picture5_upload_time.png", 
                caption="圖5：上傳打卡記錄介面")
        
        st.divider()
        
        # Step 3: Verify and download
        st.markdown("### ✅ 步驟 3：確認並下載薪資報表")
        st.markdown("""
        1. 確認預覽資料中各員工 **"平均薪資"** 是否正確
        2. 如有錯誤，請至 **"員工管理"** 中修改
        3. 資料確認無誤後，點擊 **"下載完整薪資報表(Excel)"** 下載資料
        """)
        
        st.error("""
        ⚠️ **重要提醒**：
        
        請務必確認平均薪資正確，這會直接影響加班費計算！
        """)
        
        # Placeholder for Picture6
        st.image("tutorial_images/picture6_salary_result.png", 
                caption="圖6：薪資計算結果預覽")
    
    st.divider()
    
    # Tips and Best Practices
    st.header("💡 使用小技巧")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **✅ 最佳實踐**
        
        1. 每月固定時間處理資料
        2. 保留所有員工歷史記錄
        3. 定期檢查員工薪資是否有更新
        4. 處理前先備份原始資料
        """)
    
    with col2:
        st.warning("""
        **⚠️ 常見錯誤**
        
        1. 員工綽號與打卡記錄不一致
        2. 打卡記錄缺少配對（只有上班沒下班）
        3. 日期時間格式不正確
        4. 忘記更新員工平均薪資
        """)
    
    st.divider()
    
    # FAQ Section
    st.header("❓ 常見問題")
    
    with st.expander("Q1: 如果員工綽號和打卡記錄名字不一致怎麼辦？"):
        st.markdown("""
        請至 **"員工管理"** → **"更新員工資料"**，確保綽號與打卡系統中的名字完全一致。
        
        系統會根據綽號配對員工資料，如果不一致會導致無法計算該員工的薪資。
        """)
    
    with st.expander("Q2: 如何處理缺少配對的打卡記錄？"):
        st.markdown("""
        1. 在 Excel 中找到缺少配對的記錄
        2. 插入新的一列
        3. 填入對應的上班或下班時間
        4. 格式：`yyyy-MM-dd HH:mm:ss`，例如：`2025-04-25 09:46:27`
        """)
    
    with st.expander("Q3: 平均薪資是如何計算的？"):
        st.markdown("""
        預設計算方式：**月薪 ÷ 30天 ÷ 8小時**
        
        例如：月薪 30,000 → 平均薪資 = 30,000 ÷ 30 ÷ 8 = 125
        
        您也可以在員工管理中手動調整平均薪資。
        """)
    
    with st.expander("Q4: 加班費是如何計算的？"):
        st.markdown("""
        **加班費計算規則：**
        
        - **8-10小時**：時薪 × 1.33
        - **10-12小時**：時薪 × 1.67
        - **超過12小時**：請注意！系統目前僅計算到12小時
        
        時薪 = 平均薪資
        """)
    
    with st.expander("Q5: 可以查看歷史薪資記錄嗎？"):
        st.markdown("""
        目前系統會保存最近 **5年** 的薪資和POS資料。
        
        您可以在各功能的 **"歷史記錄"** 標籤中查看和下載過往資料。
        """)
    
    st.divider()
    
    # Contact and Support
    st.header("📞 需要幫助？")
    
    st.info("""
    如果您在使用過程中遇到任何問題，請聯繫系統管理員。
    
    **提供問題時請包含：**
    - 您在執行什麼操作
    - 遇到什麼錯誤訊息
    - 錯誤發生的時間
    - 相關截圖（如有）
    """)
    
    # Navigation tips
    st.divider()
    st.success("""
    ✅ **準備好開始了嗎？**
    
    請使用左側選單選擇您需要的功能，祝您使用愉快！
    """)


if __name__ == "__main__":
    show_tutorial()