import streamlit as st
import os
import json
import pdfplumber
from llm_providers import AnthropicProvider, GeminiProvider

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

# Helper function to prepare the message content
def prepare_message_content(resume, job_description, company_info):
    return (
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

# Updated function to generate the optimized resume, compare changes, and provide a new score
def optimize_and_compare_resume(resume, job_description, company_info, suggestions, provider):
    message_content = (
        "You are an expert resume optimizer. Using the feedback and suggestions provided, optimize the following resume:\n\n"
        f"Resume:\n{resume}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Company Information:\n{company_info}\n\n"
        f"Suggestions:\n{suggestions}\n\n"
        "Please provide an optimized version of the resume. After that, provide a detailed list of changes made, including additions, modifications, and removals. Finally, provide a new score out of 100 for the optimized resume. Format your response as follows:\n\n"
        "<optimized_resume>\n[Insert the optimized resume here]\n</optimized_resume>\n\n"
        "<changes_made>\n"
        "- [List each significant change, addition, or removal]\n"
        "- [Be specific about what was changed and why]\n"
        "</changes_made>\n\n"
        "<new_score>\n"
        "[Provide a new score out of 100 for the optimized resume, considering how well it now matches the job description and company information]\n"
        "</new_score>\n\n"
        "<score_justification>\n"
        "[Explain why you gave this new score, highlighting improvements and any remaining areas for potential enhancement]\n"
        "</score_justification>"
    )

    response = provider.analyze_resume(message_content)
    
    # Extract optimized resume, changes, new score, and justification
    optimized_start = response.find("<optimized_resume>") + len("<optimized_resume>\n")
    optimized_end = response.find("</optimized_resume>")
    optimized_resume = response[optimized_start:optimized_end].strip()

    changes_start = response.find("<changes_made>") + len("<changes_made>\n")
    changes_end = response.find("</changes_made>")
    changes_made = response[changes_start:changes_end].strip()

    new_score_start = response.find("<new_score>") + len("<new_score>\n")
    new_score_end = response.find("</new_score>")
    new_score = response[new_score_start:new_score_end].strip()

    justification_start = response.find("<score_justification>") + len("<score_justification>\n")
    justification_end = response.find("</score_justification>")
    new_score_justification = response[justification_start:justification_end].strip()

    return optimized_resume, changes_made, new_score, new_score_justification

# Streamlit app
st.title("AI Resume Enhancer")

# Add provider selection
provider_options = ["Anthropic", "Google Gemini"]
selected_provider = st.selectbox("Select AI Provider", provider_options)

# Function to handle input for each section
def get_input(section_name):
    input_method = st.radio(f"Choose input method for {section_name}", ["Upload File", "Paste Text"])
    
    if input_method == "Upload File":
        uploaded_file = st.file_uploader(f"Upload {section_name} (.txt or .pdf)", type=["txt", "pdf"], key=f"{section_name}_file")
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                return read_pdf(uploaded_file)
            else:
                return uploaded_file.read().decode("utf-8")
    else:
        return st.text_area(f"Paste {section_name} here", key=f"{section_name}_text")
    
    return ""

# Get input for each section
resume = get_input("Resume")
job_description = get_input("Job Description")
company_info = get_input("Company Information")

# Store the parsed output in session state
if 'parsed_output' not in st.session_state:
    st.session_state['parsed_output'] = None

# Button to generate the report
if st.button("Generate Report"):
    if not (resume and job_description and company_info):
        st.warning("Please provide all required information.")
    else:
        # Prepare the message content
        message_content = prepare_message_content(resume, job_description, company_info)

        try:
            if selected_provider == "Anthropic":
                provider = AnthropicProvider()
            elif selected_provider == "Google Gemini":
                provider = GeminiProvider()
            else:
                raise ValueError("Invalid provider selected")

            # Generate initial analysis
            output_text = provider.analyze_resume(message_content)
            parsed_output = parse_output(output_text)

            # Optimize resume and get changes
            optimized_resume, changes_made, new_score, new_score_justification = optimize_and_compare_resume(
                resume, job_description, company_info, parsed_output["tailoring_suggestions"], provider
            )

            # Combine all results
            final_output = {
                "initial_analysis": parsed_output,
                "optimized_resume": optimized_resume,
                "changes_made": changes_made,
                "initial_score": parsed_output["score"],
                "new_score": new_score,
                "new_score_justification": new_score_justification
            }

            # Store the final output in session state
            st.session_state['parsed_output'] = final_output

            # Display the response in JSON format
            st.subheader("AI Analysis, Optimization, and Changes")
            st.json(final_output)

            # Display score improvement
            st.subheader("Resume Score Improvement")
            initial_score = int(parsed_output["score"].split("/")[0])
            new_score = int(new_score.split("/")[0])
            score_diff = new_score - initial_score
            st.write(f"Initial Score: {initial_score}/100")
            st.write(f"New Score: {new_score}/100")
            st.write(f"Improvement: {score_diff} points")

            # Button to download the JSON response
            json_data = json.dumps(final_output, indent=4)
            st.download_button(
                label="Download Full Report (JSON)",
                data=json_data,
                file_name='resume_analysis_and_optimization.json',
                mime='application/json'
            )

            # Display optimized resume and offer download
            st.subheader("Optimized Resume")
            st.text_area("Optimized Resume", optimized_resume, height=300)
            st.download_button(
                label="Download Optimized Resume",
                data=optimized_resume,
                file_name='optimized_resume.txt',
                mime='text/plain'
            )

        except Exception as e:
            st.error(f"Error: {str(e)}")