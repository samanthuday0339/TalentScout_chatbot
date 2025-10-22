"""
TalentScout AI Hiring Assistant - Prompts and Logic
Defines sequential questions, fallbacks, and dynamic tech question generation.
"""

QUESTIONS = [
    {"key": "name", "text": "👋 Hi! I’m TalentScout, your AI hiring assistant. Please enter your full name (letters and spaces only)."},
    {"key": "email", "text": "Nice to meet you, {name}! Please provide a valid email address (e.g., user@example.com)."},
    {"key": "phone", "text": "Thanks, {name}! Please share your phone number (e.g., +1234567890 or 1234567890)."},
    {"key": "experience", "text": "Got it! How many years of experience do you have, {name}? (Enter a number, e.g., 3)."},
    {"key": "position", "text": "Perfect. What position or role are you applying for, {name}? (At least 3 characters, e.g., AI Engineer)."},
    {"key": "location", "text": "Great! Where are you currently located, {name}? (At least 3 characters, e.g., New York)."},
    {"key": "techstack", "text": "Awesome! Please list your tech stack — programming languages, frameworks, and tools you use most (e.g., Python, Django, TensorFlow)."}
]

FALLBACK = "Sorry, I didn’t understand that. Could you please rephrase or provide the requested detail?"
THANK_YOU = "🎉 Thank you, {name}! Our TalentScout team will review your responses and contact you soon. Have a great day! 😊"

def generate_tech_questions(techstack: str):
    """
    Generates 3-5 technical questions based on the candidate's tech stack.
    
    Args:
        techstack (str): Comma-separated string of technologies (e.g., "Python, Django").
    
    Returns:
        list: List of technical questions tailored to the tech stack.
    """
    techstack = techstack.lower()
    questions = []

    if "python" in techstack:
        questions += [
            "What are Python decorators and how are they used in practice?",
            "Explain the difference between deep copy and shallow copy in Python.",
            "How does Python’s Global Interpreter Lock (GIL) impact multi-threading?"
        ]
    if "django" in techstack:
        questions += [
            "What is the role of Django’s ORM in handling database operations?",
            "Explain how Django’s middleware processes requests and responses.",
            "How do you optimize Django queries for performance?"
        ]
    if "machine learning" in techstack or "ml" in techstack or "tensorflow" in techstack:
        questions += [
            "What techniques can you use to prevent overfitting in machine learning models?",
            "Explain the difference between supervised and unsupervised learning.",
            "How does TensorFlow’s computational graph work?"
        ]
    if "react" in techstack:
        questions += [
            "What are React hooks and how do they simplify state management?",
            "How does React’s reconciliation process optimize rendering?",
            "What is the difference between controlled and uncontrolled components in React?"
        ]
    if "java" in techstack:
        questions += [
            "What is the difference between an abstract class and an interface in Java?",
            "Explain the role of the JVM in Java’s platform independence.",
            "How does Java’s garbage collector work?"
        ]
    if "sql" in techstack:
        questions += [
            "What is the difference between INNER JOIN and LEFT JOIN in SQL?",
            "How would you optimize a slow-running SQL query?",
            "Explain the concept of database normalization."
        ]
    if not questions:
        questions = [
            "Could you describe a recent project where you used your mentioned tech stack?",
            "What challenges did you face while working with your tech stack?",
            "How do you stay updated with advancements in your tech stack?"
        ]
    
    # Limit to 3-5 questions
    return questions[:5]
