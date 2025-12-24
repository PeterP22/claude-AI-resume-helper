# AI Resume Optimizer

Automatically tailor resumes to job descriptions using Claude and Gemini LLMs.

## Features

- **Job Analysis**: Extracts key requirements, skills, and keywords from job descriptions
- **Resume Optimization**: Rewrites bullets using the X-Y-Z formula (Google's proven method)
- **Quantitative Scoring**: Before/after comparison with detailed metrics
- **Multi-Provider Support**: Choose between Anthropic Claude or Google Gemini
- **PDF Export**: ATS-optimized formatting for maximum compatibility

## How It Works

```
Resume + Job Description → AI Analysis → Optimized Resume + Score Report
```

1. **Upload** your resume (PDF or TXT) and paste the job description
2. **Analyze**: AI extracts job requirements and evaluates your current resume
3. **Optimize**: Generates tailored bullet points emphasizing relevant experience
4. **Compare**: View quantitative score improvements across multiple dimensions
5. **Export**: Download optimized resume and detailed JSON analysis report

## Quick Start

```bash
# Clone the repository
git clone https://github.com/PeterP22/claude-AI-resume-helper.git
cd claude-AI-resume-helper

# Install dependencies
pip install -r requirements.txt

# Set your API keys
export ANTHROPIC_API_KEY=your_key_here
export GOOGLE_API_KEY=your_key_here

# Run the application
streamlit run app.py
```

## Tech Stack

- **LLMs**: Anthropic Claude 3.5, Google Gemini
- **Frontend**: Streamlit
- **File Processing**: PDF parsing, text extraction
- **Export**: JSON reports, optimized resume download

## Scoring Dimensions

The optimizer evaluates resumes across multiple criteria:

| Dimension | Description |
|-----------|-------------|
| Keyword Match | Alignment with job description keywords |
| Impact Metrics | Quantified achievements (X-Y-Z formula) |
| Relevance | Experience alignment with role requirements |
| ATS Compatibility | Format and keyword optimization |

## License

MIT
