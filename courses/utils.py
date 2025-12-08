import os
import google.generativeai as genai
import PyPDF2
from django.conf import settings
from dotenv import load_dotenv
import io

load_dotenv()

def setup_gemini():
    """Setup Gemini API with correct model"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    
    # Try available models in order
    available_models = [
        'models/gemini-2.0-flash',        # ✅ Recommended - stable
        'models/gemini-2.0-flash-001',    # ✅ Specific stable version
        'models/gemini-2.5-flash',        # ✅ Newer version
        'models/gemini-2.0-flash-lite',   # ✅ Lite version
        'models/gemini-pro-latest',       # ✅ Latest pro
    ]
    
    for model_name in available_models:
        try:
            print(f"🔍 Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            # Quick test
            response = model.generate_content("Hello")
            print(f"✅ Successfully connected to model: {model_name}")
            return model
        except Exception as e:
            print(f"❌ Model {model_name} failed: {str(e)[:100]}...")
            continue
    
    # If all fail, raise error
    raise ValueError("No working Gemini model found. Check your API key and model availability.")

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        # Reset file pointer to beginning
        if hasattr(pdf_file, 'seek'):
            pdf_file.seek(0)
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        # Extract text from each page (limit to 10 pages)
        for page_num in range(min(len(pdf_reader.pages), 10)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # Limit to 15000 characters for API
        return text[:15000]
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def generate_quiz_from_pdf(pdf_text, course_name, instructor_name, pdf_title, num_questions=5, difficulty='medium'):
    """Generate quizzes from PDF text using Gemini"""
    
    difficulty_map = {
        'easy': 'easy questions suitable for beginners',
        'medium': 'moderately difficult questions',
        'hard': 'challenging questions that test deep understanding'
    }
    
    prompt = f"""
    Based on the following PDF content from a course, generate {num_questions} multiple-choice quizzes.
    
    Course: {course_name}
    Instructor: {instructor_name}
    PDF Title: {pdf_title}
    Difficulty Level: {difficulty_map.get(difficulty, 'moderately difficult questions')}
    Number of Questions: {num_questions}
    
    PDF Content:
    {pdf_text}
    
    Generate exactly {num_questions} quizzes with the following format for EACH quiz:
    
    QUESTION: [The question text]
    OPTION_A: [Option A]
    OPTION_B: [Option B]
    OPTION_C: [Option C]
    OPTION_D: [Option D]
    CORRECT_ANSWER: [A/B/C/D]
    
    IMPORTANT: 
    1. Use this EXACT format for each quiz
    2. Separate each quiz with a blank line
    3. Only output the quizzes, no additional text
    4. Each question should test important concepts from the PDF
    5. Options should be plausible but only one correct
    6. Questions should cover different parts of the content
    
    Now generate {num_questions} quizzes:
    """
    
    try:
        model = setup_gemini()
        response = model.generate_content(prompt)
        
        # Debug output
        print(f"\n{'='*50}")
        print("Raw response from Gemini:")
        print(response.text[:500])
        print(f"{'='*50}\n")
        
        quizzes = parse_quiz_response(response.text)
        print(f"✅ Parsed {len(quizzes)} quizzes from response")
        
        # If no quizzes parsed, generate mock data
        if not quizzes:
            print("⚠️ No quizzes parsed, generating mock data")
            return generate_mock_quizzes(course_name, num_questions)
            
        return quizzes
    except Exception as e:
        print(f"❌ Error generating quiz: {e}")
        # Fallback to mock data
        return generate_mock_quizzes(course_name, num_questions)

def parse_quiz_response(response_text):
    """Parse Gemini response into quiz dictionaries"""
    quizzes = []
    lines = response_text.strip().split('\n')
    
    current_quiz = {}
    for line in lines:
        line = line.strip()
        
        if line.startswith('QUESTION:'):
            if current_quiz:
                quizzes.append(current_quiz)
            current_quiz = {'question': line.replace('QUESTION:', '').strip()}
        elif line.startswith('OPTION_A:'):
            current_quiz['option_a'] = line.replace('OPTION_A:', '').strip()
        elif line.startswith('OPTION_B:'):
            current_quiz['option_b'] = line.replace('OPTION_B:', '').strip()
        elif line.startswith('OPTION_C:'):
            current_quiz['option_c'] = line.replace('OPTION_C:', '').strip()
        elif line.startswith('OPTION_D:'):
            current_quiz['option_d'] = line.replace('OPTION_D:', '').strip()
        elif line.startswith('CORRECT_ANSWER:'):
            current_quiz['correct_answer'] = line.replace('CORRECT_ANSWER:', '').strip()
    
    # Add the last quiz
    if current_quiz:
        quizzes.append(current_quiz)
    
    # Validate quizzes have all required fields
    valid_quizzes = []
    for quiz in quizzes:
        if all(key in quiz for key in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']):
            valid_quizzes.append(quiz)
        else:
            print(f"⚠️ Incomplete quiz skipped: {quiz}")
    
    return valid_quizzes[:10]  # Return max 10 quizzes

def generate_mock_quizzes(course_name, num_questions=5):
    """Generate mock quizzes for testing when API fails"""
    quizzes = []
    for i in range(min(num_questions, 5)):
        quizzes.append({
            'question': f"What is a key learning objective from the {course_name} course? (Mock Question {i+1})",
            'option_a': 'Understanding fundamental concepts',
            'option_b': 'Mastering advanced techniques',
            'option_c': 'Learning historical context',
            'option_d': 'Applying knowledge in real scenarios',
            'correct_answer': 'A' if i % 4 == 0 else 'B' if i % 4 == 1 else 'C' if i % 4 == 2 else 'D'
        })
    
    print(f"✅ Generated {len(quizzes)} mock quizzes for development")
    return quizzes

# Alternative simple setup (if above doesn't work)
def setup_gemini_simple():
    """Simple setup using most reliable model"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    
    # Use gemini-2.0-flash (most reliable from your list)
    try:
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        print("✅ Using model: models/gemini-2.0-flash")
        return model
    except Exception as e:
        print(f"❌ models/gemini-2.0-flash failed: {e}")
    
    # Fallback
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        print("✅ Using model: models/gemini-2.5-flash")
        return model
    except Exception as e:
        print(f"❌ models/gemini-2.5-flash failed: {e}")
    
    raise ValueError("Could not initialize any Gemini model")