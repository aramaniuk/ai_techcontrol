import streamlit as st
from openai import OpenAI
import base64
import fitz  # PyMuPDF
import os

# Page configuration
st.set_page_config(page_title="AI помощник инженера-проектировщика", layout="wide")

def get_regulations():
    """Reads the local regulations file."""
    reg_path = "snips/СН-РК-5.03-07-2013.txt"
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            return f.read()
    return "No standard regulations file found."

# Sidebar for inputs
with st.sidebar:
    st.title("Settings")

    # File upload
    uploaded_file = st.file_uploader("Загрузите проектную документацию", type=['txt', 'pdf', 'md', 'png', 'jpg', 'jpeg'])

    # Analysis options
    analysis_option = st.selectbox(
        "Выберите тип анализа",
        options=["Structural Integrity Check", "Material Standard Compliance", "Safety Regulation Audit"],
        index=0
    )
    
    # Run button
    analyze_button = st.button("Запустить анализ", disabled=not uploaded_file)

# Main Pane
st.title("AI анализ структуры строительного проекта")

if analyze_button:
    api_key = st.secrets["openai"]["OPENAI_API_KEY"]

    if not api_key:
        st.error("Please provide an OpenAI API Key.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            regulations_content = get_regulations()

            # Read file content
            file_bytes = uploaded_file.read()
            file_extension = uploaded_file.name.split('.')[-1].lower()

            with st.spinner("Анализирую спецификацию относительно стандартов..."):
                prompt_text = (
                    f"You are provided with a construction technical specification and a set of standard regulations.\n\n"
                    f"REGULATIONS FOR REFERENCE:\n{regulations_content}\n\n"
                    f"TASK:\nAnalyze the uploaded specification based on: {analysis_option}.\n"
                    f"Identify if the specification complies with the regulations provided above. "
                    f"Highlight specific discrepancies or safety risks found in the document (text or images). Response should be generated in Russian"
                )

                content = [{"type": "text", "text": prompt_text}]

                if file_extension == 'pdf':
                    pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
                    for page_index in range(len(pdf_doc)):
                        page = pdf_doc.load_page(page_index)
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    
                        img_bytes = pix.tobytes("jpeg")
                        base_64_page = base64.b64encode(img_bytes).decode('utf-8')
                    
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base_64_page}",
                                "detail": "high"
                            }
                        })
                    pdf_doc.close()
                elif file_extension in ['png', 'jpg', 'jpeg']:
                    # Handle standard image formats
                    base64_file = base64.b64encode(file_bytes).decode('utf-8')
                    mime_type = f"image/{file_extension}"
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_file}"
                        }
                    })
                else:
                    # Handle text files (txt, md)
                    text_content = file_bytes.decode("utf-8")
                    content.append({
                        "type": "text",
                        "text": f"Document Text Content:\n{text_content}"
                    })

                # LLM Call
                response = client.chat.completions.create(
                    model="gpt-5.2-2025-12-11",
                    messages=[
                        {"role": "system", "content": "You are an expert construction engineer and auditor."},
                        {"role": "user", "content": content}
                    ]
                )

                # Display Results
                st.subheader(f"Analysis Results: {analysis_option}")
                st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.info("Загрузите проектный файл и выберите тип анализа для начала работы....")
