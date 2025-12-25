import streamlit as st
from openai import OpenAI
import base64
from io import BytesIO
import fitz  # This will now correctly import PyMuPDF after the pip changes


# Page configuration
st.set_page_config(page_title="Construction Spec Validator", layout="wide")

# Sidebar for inputs
with st.sidebar:
    st.title("Settings")
    
    # API Key input (standard practice for local/dev Streamlit apps)
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Technical Specification", type=['txt', 'pdf', 'md', 'png', 'jpg', 'jpeg'])

    # Analysis options
    analysis_option = st.selectbox(
        "Select Analysis Type",
        options=["Structural Integrity Check", "Material Standard Compliance", "Safety Regulation Audit"],
        index=0
    )
    
    # Run button
    analyze_button = st.button("Start Analysis", disabled=not uploaded_file)

# Main Pane
st.title("Construction Project Analysis")

if analyze_button:
    if not api_key:
        st.error("Please provide an OpenAI API Key in the sidebar.")
    else:
        try:
            client = OpenAI(api_key=api_key)
                
                # Read file content
            file_bytes = uploaded_file.read()
            file_extension = uploaded_file.name.split('.')[-1].lower()

            with st.spinner("Analyzing specification against standards..."):
                prompt_text = (
                    f"Analyze the following construction technical specification based on: {analysis_option}.\n"
                    f"Validate it against standard construction industry benchmarks and highlight discrepancies.\n"
                    f"Parse both text and graphic materials in the document."
                )

                content = [{"type": "text", "text": prompt_text}]

                if file_extension == 'pdf':
                    # This call will now work correctly
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
                # rest of the code
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
                    model="gpt-4o",
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
    st.info("Upload a file and select an analysis type from the sidebar to begin.")
