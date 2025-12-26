import streamlit as st
from validator_engine import analyze_compliance

# Page configuration
st.set_page_config(page_title="AI помощник инженера-проектировщика", layout="wide")

# Sidebar for inputs
with st.sidebar:
    st.title("Настройки")

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
        st.error("Предоставьте ключ OpenAI API.")
    else:
        try:
            # Read file content
            file_bytes = uploaded_file.read()
            file_extension = uploaded_file.name.split('.')[-1].lower()

            with st.spinner("Анализирую спецификацию относительно стандартов..."):

                analysis_result = analyze_compliance(file_bytes, file_extension, analysis_option)
                # Display Results
                st.subheader(f"Результат анализа спецификации по выбранной опции: {analysis_option}")
                st.markdown(analysis_result)
            
        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
else:
    st.info("Загрузите проектный файл и выберите тип анализа для начала работы....")
