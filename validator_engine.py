import base64
import os
import fitz
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from llm_factory import LLMFactory

# 1. Initialize the wrapper (Easy Shift happens here)
# Toggle this string to switch providers later
PROVIDER_MODE = "OPENAI"
llm = LLMFactory.get_model(mode=PROVIDER_MODE)

def get_regulations():
    """Reads the local regulations file."""
    reg_path = "snips/СН-РК-5.03-07-2013.txt"
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Стандартные технические регламенты не найдены."

def analyze_compliance(file_bytes, file_extension, analysis_option):
    """
    Analyzes construction documents against regulations using LangChain.
    """
    regulations_content = get_regulations()

    prompt_text = (
        f"You are provided with a construction technical specification and a set of standard regulations.\n\n"
        f"REGULATIONS FOR REFERENCE:\n{regulations_content}\n\n"
        f"TASK:\nAnalyze the uploaded specification based on: {analysis_option}.\n"
        f"Identify if the specification complies with the regulations provided above. "
        f"Highlight specific discrepancies or safety risks found in the document (text or images). "
        f"If a violation is found, cite the specific Standard Clause. " 
        f"Return result as a structured Summary. "
        f"Response should be generated in Russian. "
    )

    # Prepare content for multi-modal input
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
                "image_url": {"url": f"data:image/jpeg;base64,{base_64_page}"}
            })
        pdf_doc.close()
    elif file_extension in ['png', 'jpg', 'jpeg']:
        base64_file = base64.b64encode(file_bytes).decode('utf-8')
        mime_type = f"image/{file_extension}"
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{base64_file}"}
        })
    else:
        text_content = file_bytes.decode("utf-8")
        content.append({"type": "text", "text": f"Document Text Content:\n{text_content}"})

    # 1. Define Messages
    messages = [
        SystemMessage(content=f"You are a Senior Structural Engineer."
            f"Verify if the construction schema complies with the provided National Standards."),
        HumanMessage(content=content)
    ]

    # 2. Create Chain (StrOutputParser ensures we get a string back)
    chain = llm | StrOutputParser()

    # 3. Execute
    result = chain.invoke(messages)

    return result