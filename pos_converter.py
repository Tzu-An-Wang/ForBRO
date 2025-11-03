import pandas as pd
import streamlit as st
from io import BytesIO

def run_pos_converter():
    st.title('POS 轉 Excel')
    
    # File upload
    uploaded_file = st.file_uploader('請上傳 POS 資料', type = 'xlsx')
    if uploaded_file is not None:
        excel = pd.ExcelFile(uploaded_file)
        df1 = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        final_Sheet1 = df1[df1["Unnamed: 1"] == "小結"].iloc[:, [2, 3]]
        final_Sheet1["時間"] = pd.to_datetime(final_Sheet1.iloc[:, 0])
        final_Sheet1 = final_Sheet1.sort_values(by="時間", ascending=True)
        final_Sheet1["時間"] = final_Sheet1["時間"].dt.strftime('%Y/%-m/%-d')
        final_Sheet1["累積營收/現金"] = final_Sheet1.iloc[:, 1].cumsum()
        final_Sheet1["備註"] = ""

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("預覽資料")
            st.dataframe(final_Sheet1)
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            final_Sheet1.to_excel(writer, sheet_name='Sheet1')

        with col2:
            st.download_button(
                label="點此下載",
                data=buffer.getvalue(),
                file_name="修改後資料.xlsx",
                mime="application/vnd.ms-excel"
            )