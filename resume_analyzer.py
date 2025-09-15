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
    st.set_page_config(
        page_title="Resume Analysis Pro",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for a more professional look
    st.markdown("""
    <style>
        /* General styling */
        .stApp {
            background-color: #f0f2f6;
        }
        /* Sidebar styling */
        .st-emotion-cache-16txtl3 {
            background-color: #ffffff;
            border-right: 1px solid #e6e6e6;
        }
        /* Main content styling */
        .st-emotion-cache-1y4p8pa {
            padding-top: 2rem;
        }
        /* Button styling */
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            transition-duration: 0.4s;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        /* Text area styling */
        .stTextArea textarea {
            border: 1px solid #e6e6e6;
            border-radius: 8px;
        }
        /* Header styling */
        h1, h2, h3 {
            color: #333333;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png", width=100)
        st.title("Resume Analysis Pro")
        st.markdown("---")
        st.header("Configuration")
        
        target_position = st.selectbox(
            "Target Position",
            target_positions,
            help="Select the job position you are applying for."
        )

        st.markdown("---")
        st.header("Upload or Paste Resume")
        
        uploaded_file = st.file_uploader(
            "Upload PDF, Word or TXT file",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed"
        )
        
        resume_text_area = st.text_area(
            "Or paste your resume text here",
            height=250,
            placeholder="Paste your resume content here..."
        )

        if st.button("Analyze Resume", use_container_width=True):
            resume_content = get_resume_content(uploaded_file, resume_text_area)
            if not resume_content:
                st.error("Please upload a resume file or paste the text.")
            else:
                with st.spinner("Analyzing... Please wait..."):
                    st.session_state.analysis_result = analyze_resume_with_ai(resume_content, target_position)

    # --- Main Content ---
    st.title("📄 Resume Analysis Dashboard")
    st.markdown("Welcome to the Resume Analysis Dashboard. Upload your resume and select a target position to get an AI-powered analysis.")

    col1, col2 = st.columns([2, 3])

    with col1:
        st.header("Your Resume")
        resume_content = get_resume_content(uploaded_file, resume_text_area)
        if resume_content:
            st.text_area("Resume Content", resume_content, height=600, disabled=True, label_visibility="collapsed")
        else:
            st.info("Please upload or paste your resume in the sidebar to see the content here.")

    with col2:
        st.header("Analysis Result")
        if 'analysis_result' in st.session_state and st.session_state.analysis_result:
            st.markdown(st.session_state.analysis_result)
        else:
            st.info("The analysis result will be displayed here once the analysis is complete.")

    # --- Footer ---
    st.markdown("---")
    st.markdown(
        "Powered by [Streamlit](https://streamlit.io) and [OpenAI](https://openai.com)"
    )

if __name__ == "__main__":
    main()
