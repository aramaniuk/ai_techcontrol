import streamlit as st
from openai import OpenAI

# Page configuration
st.set_page_config(page_title="Construction Spec Validator", layout="wide")

# Sidebar for inputs
with st.sidebar:
    st.title("Settings")
    
    # API Key input (standard practice for local/dev Streamlit apps)
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Technical Specification", type=['txt', 'pdf', 'md'])
    
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
            file_content = uploaded_file.read().decode("utf-8")
            
            with st.spinner("Analyzing specification against standards..."):
                # Prepare the prompt based on selection
                prompt = (
                    f"Analyze the following construction technical specification based on: {analysis_option}.\n"
                    f"Validate it against standard construction industry benchmarks and highlight discrepancies.\n\n"
                    f"Document Content:\n{file_content}"
                )
                
                # LLM Call
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert construction engineer and auditor."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Display Results
                st.subheader(f"Analysis Results: {analysis_option}")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.info("Upload a file and select an analysis type from the sidebar to begin.")
