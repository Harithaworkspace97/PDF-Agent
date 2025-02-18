import streamlit as st
from unstructured.partition.pdf import partition_pdf
from openai import OpenAI
import os
import glob
import shutil
import tempfile

# Title of the app
st.title("PDF Content Viewer with LLM")

# LLM Authentication
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="API-KEY",
)

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Save the uploaded file temporarily
    filename = "temp.pdf"
    with open(filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # Extract elements using `hi_res` strategy
        elements = partition_pdf(
            filename=filename,
            strategy="hi_res",
            extract_images_in_pdf=False,
            infer_table_structure=True,
            ocr_languages="eng",
        )

        # Combine extracted text
        document_text = "\n".join(
            [
                el.text.strip()
                for el in elements
                if el.category in ["Title", "NarrativeText"]
            ]
        )

        # Display extracted text
        # **Prompt Input Section**
        st.subheader("Ask a Question About the PDF")
        query = st.text_input("Enter your prompt or question:")

        if query:
            # LLM Query
            response = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional
                    "X-Title": "<YOUR_SITE_NAME>",  # Optional
                },
                model="deepseek/deepseek-r1-distill-llama-70b:free",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": f"Context: {document_text}\n\nQuestion: {query}",
                    },
                ],
            )
            llm_response = response.choices[0].message.content

            st.subheader("🤖 LLM Response")
            st.write(llm_response)

    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        # Cleanup temporary file
        os.remove(filename)
