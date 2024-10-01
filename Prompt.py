import datetime
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Template for Socratic Questions related to Data Structures and Algorithms
socraticTemplate = """
Socrates DS Assistant is an AI-powered teaching assistant designed to help students learn Data Structures and Algorithms (DSA) through critical thinking and reflection. It uses the Socratic method to guide learners to discover solutions themselves through deep, probing questions.

### Instructions for the AI Assistant:
1. Ask open-ended questions about sorting algorithms, data structures, or algorithmic complexity.
2. Evaluate the student's responses based on a five-level classification:
   - Fully Correct
   - Correct but Lacking Depth
   - Correct but Misleading
   - Partially Incorrect
   - Incorrect
3. Guide the student through reflection without providing direct answers, but instead use further probing questions to explore misconceptions or deepen understanding.

Here is the input data for the student:

- Concept: [Concept]
- Student Response: [StudentResponse]
- Depth of Knowledge: [KnowledgeLevel]

The assistant should:
1. Start with an open-ended question about the concept.
2. After receiving the student's response, evaluate the response using the five-level classification.
3. Provide feedback and ask a follow-up question to deepen understanding or correct misconceptions.

"""

# Example function to generate Socratic questions and evaluate responses
def onMessage(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'Content-Type': 'application/json'
    }

    if request.method == 'OPTIONS':
        return ('', 204, headers)

    try:
        payload = request.json
        data = payload['data']
        concept = data.get('concept', 'Sorting Algorithms')  # Example concept
        student_response = data.get('studentResponse', '')   # Student's answer
        knowledge_level = data.get('knowledgeLevel', 'Intermediate')  # Student's knowledge level

        # Construct the user message for Socratic questioning
        message = construct_user_message(concept, student_response, knowledge_level)

        # Generate Socratic feedback and questions
        generated_copy = generate_socratic_questions(socraticTemplate, message)

        return (generated_copy, 200, headers)

    except Exception as e:
        # Respond with an error message
        error_message = f"An error occurred: {str(e)}"
        return (error_message, 500, headers)

# Construct the user message for Socratic DS Assistant
def construct_user_message(concept, student_response, knowledge_level):
    user_message = f"Concept: {concept}\n" \
                   f"Student Response: {student_response}\n" \
                   f"Knowledge Level: {knowledge_level}\n" \
                   "Guide the student using the Socratic method. Do not provide direct answers."
    return user_message

# Standardizing the feedback output for better parsing
def standardize_socratic_output(output):
    prompt = f"""
    You are tasked with standardizing the following Socratic feedback and questions to ensure clear readability. Your goal is to:
    - Label the sections clearly (e.g., Response Evaluation, Feedback, Next Question).
    - Provide a concise and structured response for the student.

    Here's the content that needs to be standardized:

    {output}

    Output format:
    ### Response Evaluation:
    [Evaluation of student's response based on five-level classification]

    ### Feedback:
    [Concise feedback based on evaluation]

    ### Next Question:
    [Follow-up question to guide the student's learning]

    Please only return the standardized Socratic feedback.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant specializing in text formatting."},
            {"role": "user", "content": prompt}
        ]
    )

    standardized_output = response.choices[0].message.content.strip()
    return standardized_output

# Generate Socratic questions and feedback
def generate_socratic_questions(template, user_message):
    # Generate initial content using the chat-based model
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": template},
            {"role": "user", "content": user_message}
        ]
    )

    initial_content = response.choices[0].message.content.strip()

    # Standardize the Socratic feedback for clarity
    standard_content = standardize_socratic_output(initial_content)

    return standard_content

