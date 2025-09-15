#! /usr/bin/env python3
'''
简历分析智能体
'''
import streamlit as st
from openai import OpenAI
import pypdf
import docx

target_positions=["前端开发","后端开发","全栈开发","数据分析师","游戏开发","游戏策划"]
def extract_file_content(uploaded_file):
    if uploaded_file is None:
        return None
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == "pdf":
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file_extension == "docx":
        doc = docx.Document(uploaded_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    elif file_extension == "txt":
        return uploaded_file.read().decode("utf-8")
    else:
        st.error("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")
        return None
def get_resume_content(uploaded_file,resume_text):
    if uploaded_file:
        return extract_file_content(uploaded_file)
    elif resume_text:
        return resume_text
    else:
        return None
def analyze_resume_with_ai(resume_text,target_position):
    client = OpenAI(api_key=st.secrets["API_KEY"], 
                    base_url="https://api.siliconflow.cn/v1")
    prompt=f"作为专业的hr顾问，请分析以下简历，判断其是否符合{target_position}的要求：{resume_text}请提供：1,总体评分(1-100分)2,详细的分析和改进建议 3，核心优势和发展建议 要求评分和建议完全基于简历内容，个性化分析，避免模板化回复"
    response = client.chat.completions.create(
    model="Qwen/Qwen3-8B",
    messages=[
        {'role': 'system', 'content': "你是一个专业的hr简历分析师，根据简历内容给出客观、个性化的分析和建议"},
        {'role': 'user', 'content': prompt}
    ],
    stream=True
)
    analysis_content = ""
    for chunk in response:
        if not chunk.choices:
            continue
        if chunk.choices[0].delta.content:
            analysis_content += chunk.choices[0].delta.content
    return analysis_content

def main():
    st.set_page_config(page_title="Resume Analysis", layout="wide")

    # Custom CSS
    st.markdown("""
    <style>
        .st-emotion-cache-1y4p8pa {
            padding-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("Resume Analysis Control Panel")
    st.sidebar.markdown("---")

    target_position = st.sidebar.selectbox(
        "选择目标岗位",
        target_positions
    )

    st.sidebar.markdown("---")
    st.sidebar.header("上传或粘贴简历")

    uploaded_file = st.sidebar.file_uploader("上传PDF、Word或TXT文档", type=["pdf", "docx", "txt"])
    resume_text_area = st.sidebar.text_area("或在此处粘贴简历文本", height=300)

    resume_content = get_resume_content(uploaded_file, resume_text_area)

    col1, col2 = st.columns([2, 3])

    with col1:
        st.header("简历内容")
        if resume_content:
            st.text_area("简历内容", resume_content, height=600, disabled=True)
        else:
            st.info("请上传简历文件或在侧边栏粘贴简历文本。")

    with col2:
        st.header("分析结果")
        if 'analysis_result' not in st.session_state:
            st.session_state.analysis_result = ""

    if st.sidebar.button("开始分析"):
        if not resume_content:
            st.sidebar.error("请上传简历文件或粘贴简历文本")
        else:
            with st.spinner("正在分析中，请稍候..."):
                st.session_state.analysis_result = analyze_resume_with_ai(resume_content, target_position)
    
    if st.session_state.analysis_result:
        with col2:
            st.markdown(st.session_state.analysis_result)

if __name__ == "__main__":
    main()
