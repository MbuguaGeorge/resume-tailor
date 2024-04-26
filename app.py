from dotenv import load_dotenv
import streamlit as st
import os
import boto3
import pickle
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores.faiss import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI

# AWS S3 config
s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

def save_vector_store_to_s3(file_name, vector_store):
  bucket_name = os.getenv('bucket-name')
  vector_store_bytes = pickle.dumps(vector_store)
  s3.put_object(Bucket=bucket_name, Key=file_name, Body=vector_store_bytes)

def load_vector_store_from_s3(file_name):
  bucket_name = os.getenv('bucket-name')
  obj = s3.get_object(Bucket=bucket_name, Key=file_name)
  return pickle.loads(obj['Body'].read())

def s3_file_exists(file_name):
  bucket_name = os.getenv('bucket-name')
  try:
      s3.head_object(Bucket=bucket_name, Key=file_name)
      return True
  except:
      return False

llm = GoogleGenerativeAI(temperature=0, model="models/text-bison-001")

def generate_resume_text(vectorStore):
  prompt = """From the uploaded file, I need to determine its type. 
  If it's a resume, generate the file as text and format it well with 
  the corresponding titles, if it's something else, return None."""

  docs = vectorStore.similarity_search(query=prompt, k=3)

  chain = load_qa_chain(llm=llm, chain_type='stuff')
  response = chain.run(input_documents=docs, question=prompt)

  return response

def tailor_resume(vectorStore, query):
  resume_text = generate_resume_text(vectorStore)

  prompt = f"Given the following resume: \n {resume_text} \n and job description: \n {query} \n, your task is to generate a tailored resume that aligns closely with the job requirements and is optimized for Applicant Tracking Systems (ATS). The goal is to ensure that the resume effectively showcases the candidate's relevant skills and experiences, increasing the likelihood of passing through automated screening processes. Please consider the key skills and qualifications mentioned in the job description, and modify the resume accordingly to enhance its ATS compatibility."
  response = llm.invoke(prompt)

  return response

def generate_cover_letter(res, query):
  prompt = f"Resume: \n {res} \n Job description: \n {query} \n. Using the provided resume and job description, your task is to craft a compelling cover letter that effectively highlights the candidate's relevant experiences, skills, and qualifications for the position. The cover letter should serve as a personalized introduction to the candidate, showcasing their enthusiasm for the role and demonstrating how their background aligns with the company's needs. Pay close attention to the specific requirements and preferences outlined in the job description, and tailor the content of the cover letter accordingly to make a strong impression on the hiring manager."

  response = llm.invoke(prompt)

  return response

def main():
  load_dotenv()

  st.header('Resume Tailor')
  
  # upload resume
  pdf = st.file_uploader('Upload your Resume (PDF)', type='pdf')

  if pdf is not None:
    pdf_reader = PdfReader(pdf)
    
    text = ""
    for page in pdf_reader.pages:
      text += page.extract_text()

    text_splitter= RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200,
      length_function=len
    )

    chunks = text_splitter.split_text(text=text)

    # creating embeddings
    store_name = pdf.name[:-4]

    if s3_file_exists(f"{store_name}.pkl"):
      vectorStore = load_vector_store_from_s3(f"{store_name}.pkl")
    else:
      embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
      vectorStore = FAISS.from_texts(chunks, embedding=embeddings)
      save_vector_store_to_s3(f"{store_name}.pkl", vectorStore)

    query = st.text_area("Paste the job description:")
    res = tailor_resume(vectorStore, query)

    if query:      
      st.write(res)

      btn = st.button("Generate cover letter")

      if btn:
        cover_letter_res = generate_cover_letter(res, query)
        st.write(cover_letter_res)

if __name__ == '__main__':
  main()