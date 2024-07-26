import streamlit as st
import anthropic
import os
import json
import pdfplumber

# Ensure the API key is set
api_key = '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'
if not api_key or api_key == 'your_api_key_here':
    st.error("The ANTHROPIC_API_KEY environment variable is not set correctly.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# Helper function to read text from a PDF file
def read_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Helper function to parse the output into JSON
def parse_output(output):
    analysis_start = output.find("<analysis>") + len("<analysis>\n")
    analysis_end = output.find("</analysis>")
    analysis = output[analysis_start:analysis_end].strip()

    suggestions_start = output.find("<tailoring_suggestions>") + len("<tailoring_suggestions>\n")
    suggestions_end = output.find("</tailoring_suggestions>")
    suggestions = output[suggestions_start:suggestions_end].strip()

    justification_start = output.find("<score_justification>") + len("<score_justification>\n")
    justification_end = output.find("</score_justification>")
    justification = output[justification_start:justification_end].strip()

    score_start = output.find("<score>") + len("<score>\n")
    score_end = output.find("</score>")
    score = output[score_start:score_end].strip()

    return {
        "analysis": analysis,
        "tailoring_suggestions": suggestions,
        "score_justification": justification,
        "score": score
    }

# Helper function to generate the optimized resume
def optimize_resume_with_llm(resume, suggestions):
    message_content = (
        "You are an expert resume optimizer. Using the feedback and suggestions provided, optimize the following resume:\n\n"
        f"Resume:\n{resume}\n\n"
        f"Suggestions:\n{suggestions}\n\n"
        "Please provide an optimized version of the resume."
    )

    # Create the message
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message_content
                    }
                ]
            }
        ]
    )

    # Concatenate the content of the text blocks into a single string
    optimized_text = "".join([block.text for block in response.content])
    return optimized_text

st.title("AI Resume Enhancer")

# Upload fields for resume, job description, and company info
uploaded_resume = st.file_uploader("Upload your resume (.txt or .pdf)", type=["txt", "pdf"], key="resume")
uploaded_job_description = st.file_uploader("Upload the job description (.txt or .pdf)", type=["txt", "pdf"], key="job_description")
uploaded_company_info = st.file_uploader("Upload the company information (.txt or .pdf)", type=["txt", "pdf"], key="company_info")

# Read content from the uploaded files
resume = job_description = company_info = ""
if uploaded_resume:
    if uploaded_resume.type == "application/pdf":
        resume = read_pdf(uploaded_resume)
    else:
        resume = uploaded_resume.read().decode("utf-8")

if uploaded_job_description:
    if uploaded_job_description.type == "application/pdf":
        job_description = read_pdf(uploaded_job_description)
    else:
        job_description = uploaded_job_description.read().decode("utf-8")

if uploaded_company_info:
    if uploaded_company_info.type == "application/pdf":
        company_info = read_pdf(uploaded_company_info)
    else:
        company_info = uploaded_company_info.read().decode("utf-8")

# Store the parsed output in session state
if 'parsed_output' not in st.session_state:
    st.session_state['parsed_output'] = None

# Button to generate the report
if st.button("Generate Report"):
    if not (uploaded_resume and uploaded_job_description and uploaded_company_info):
        st.warning("Please upload all required files.")
    else:
        # Replace placeholders with user input
        message_content = (
            "You are an expert ATS (Applicant Tracking System) resume analyst and career advisor. Your task is to help users tailor their resumes for specific job applications by analyzing their current resume against the job description and company information provided. You will then offer suggestions for improvement and provide a score out of 100 to indicate how well the resume matches the job requirements.\n\n"
            "First, carefully review the following information:\n\n"
            f"1. The user's current resume:\n<resume>\n{resume}\n</resume>\n\n"
            f"2. The job description for the position they are applying for:\n<job_description>\n{job_description}\n</job_description>\n\n"
            f"3. Background information on the company, including details about company culture:\n<company_info>\n{company_info}\n</company_info>\n\n"
            "Now, follow these steps to analyze the resume and provide tailored advice:\n\n"
            "1. Analyze the resume in relation to the job description:\n"
            "   - Identify key skills, experiences, and qualifications mentioned in the job description.\n"
            "   - Compare these to the content of the resume.\n"
            "   - Note any missing key elements or areas where the resume could be strengthened.\n\n"
            "2. Consider the company culture and background:\n"
            "   - Identify aspects of the company culture that might be relevant to highlight in the resume.\n"
            "   - Look for ways the applicant's experience or skills align with the company's values or mission.\n\n"
            "3. Provide specific suggestions for tailoring the resume:\n"
            "   - Recommend additions, removals, or modifications to better match the job requirements.\n"
            "   - Suggest ways to incorporate relevant keywords from the job description.\n"
            "   - Advise on how to highlight experiences that align with the company culture.\n\n"
            "4. Evaluate the overall strength of the resume:\n"
            "   - Consider how well the resume matches the job requirements.\n"
            "   - Assess the clarity, organization, and professionalism of the resume.\n"
            "   - Take into account how well the resume reflects relevant aspects of the company culture.\n\n"
            "5. Determine a score out of 100:\n"
            "   - Base this score on how well the current resume matches the job and company requirements.\n"
            "   - Consider both content and presentation in your scoring.\n\n"
            "Now, provide your analysis and recommendations in the following format:\n\n"
            "<analysis>\n[Provide a detailed analysis of the resume's strengths and weaknesses in relation to the job description and company culture.]\n</analysis>\n\n"
            "<tailoring_suggestions>\n[List specific suggestions for improving the resume, including additions, removals, and modifications.]\n</tailoring_suggestions>\n\n"
            "<score_justification>\n[Explain your reasoning for the score you're about to give, highlighting key factors that influenced your decision.]\n</score_justification>\n\n"
            "<score>\n[Provide a score out of 100]\n</score>\n\n"
            "Remember to be constructive and specific in your feedback, providing actionable advice that will help the user improve their resume for this particular job application."
        )

        try:
            # Create the message
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": message_content
                            }
                        ]
                    }
                ]
            )

            # Concatenate the content of the text blocks into a single string
            output_text = "".join([block.text for block in response.content])

            # Parse the response content
            st.session_state['parsed_output'] = parse_output(output_text)

            # Display the response in JSON format
            st.subheader("AI Analysis and Recommendations")
            st.json(st.session_state['parsed_output'])

            # Button to download the JSON response
            json_data = json.dumps(st.session_state['parsed_output'], indent=4)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name='resume_analysis.json',
                mime='application/json'
            )
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Load the saved JSON response from session state
if st.session_state['parsed_output']:
    saved_analysis = st.session_state['parsed_output']

    # Button to optimize the resume
    if st.button("Optimize Resume"):
        optimized_resume = optimize_resume_with_llm(resume, saved_analysis["tailoring_suggestions"])
        st.subheader("Optimized Resume")
        st.text_area("Optimized Resume", optimized_resume, height=300)

        # Automatically download the optimized resume
        st.download_button(
            label="Download Optimized Resume",
            data=optimized_resume,
            file_name='optimized_resume.txt',
            mime='text/plain'
        )
