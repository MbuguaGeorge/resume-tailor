# Resume Tailor
Leverage generative AI technologies to streamline the resume customization process. Users can upload their resume and a job description, and our system generates a tailored resume that closely matches the job requirements. Additionally, the app optimizes resumes for Applicant Tracking Systems (ATS) to enhance visibility and increase the likelihood of passing automated screening. Crafting personalized resumes has never been easier."

## Installation

1. Clone the repository:

2. Create and activate a virtual environment:

    ```bash
    # For Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```
3.  Install the required dependencies:
   
     ```bash
    pip install -r requirements.txt
    ```
5.  Create a .env file and place your gemini Google api key

## Running the Application

1. Run the development server:

    ```bash
    streamlit run app.py
    ```

2. Access the application in your web browser at `http://localhost:8501/`
