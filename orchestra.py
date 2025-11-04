from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin # Import CORS and cross_origin
from datetime import datetime
from ollama import chat
from ollama import ChatResponse

app = Flask(__name__)
CORS(app) # Enable CORS for all routes and all origins (*)


# This is your API endpoint, matching the 'data-api-url' you set in Moodle
# For example, if your Moodle setting is "http://localhost:5000/api/chatbot"
# then the route should match "/api/chatbot"
@app.route('/api/chatbot', methods=['POST'])
def chatbot_endpoint():
    """
    Listens for POST requests from the Moodle chatbot block.
    Expects a JSON payload with 'message', 'instanceid', and 'userid'.
    """
    if not request.is_json:
        # If the request is not JSON, return an error
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Extract data sent from the Moodle block
    user_message = data.get('message', 'No message provided')
    instance_id = data.get('instanceid', 'N/A')
    userid = data.get('userid', 'N/A')
    coursedata = data.get('coursedata', 'No course data provided')
    userid = data.get('userid' , 'No user ID provided')
    firstname = data.get('firstname' , 'No firstname provided')
    lastname = data.get('lastname' , 'No lastname provided')
    courseid = data.get('courseid' , 'No courseid provided')
    coursename = data.get('coursename' , 'No coursename provided')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #parametros para o ollama
    response: ChatResponse = chat(model='gemma3:12b', messages=[
    {
        'role': 'user',
        'content': user_message,
    },
    ])
  
    #Show data in terminal
    print(f"\nCourse data: {coursedata}")

    print(f"\nUser ID: {userid}")
    print(f"\nUser Full Name: {firstname} {lastname}")
    print(f"\nCourse ID: {courseid}")
    print(f"\nCourse Name: {coursename}")
    print(f"\nTotal duration: {response.total_duration}")
    print(f"\nPrompt Eval Duration: {response.prompt_eval_duration}")
    print(f"\nEval Count: {response.eval_count}")
    print(f"\nEval Duration: {response.eval_duration}")
    eval_duration_seconds = response.eval_duration / 1e9
    tps = response.eval_count / eval_duration_seconds
    print(f"\nTokens/Sec = {tps:.2f}\n")

    # Write data to text file: Open a file in write mode ('w') or append mode ('a')
    # 'w' will create the file if it doesn't exist, and overwrite it if it does.
    # 'a' will create the file if it doesn't exist, and append to it if it does.
    with open('output.txt', 'w') as f:
    # Print a string to the file
        print("This message will be written to the file.", file=f)
        print("Another line for the file.", file=f)

    # --- Your Chatbot Logic Goes Here ---
    # In a real-world scenario, you'd integrate with:
    # - A large language model (LLM) like OpenAI, Google Gemini, etc.
    # - A rule-based chatbot engine
    # - A database to store conversation history
    # - Moodle data integration (if your API can access Moodle data securely)

    # Simple example response:
    
    bot_reply = (
        f"UID: {userid} - Instance: {instance_id} "
        f"(Received at {timestamp})"
        f"\n{response.message.content}"
    )

    # --- End Chatbot Logic ---

    # Return the response as JSON
    return jsonify({"reply": bot_reply})

# Optional: A simple root endpoint to check if the API is running

@app.route('/', methods=['GET'])
def index():
    return "Python Chatbot API is running!"

if __name__ == '__main__':
    # You might need to adjust the host and port for deployment
    # For local development, host='0.0.0.0' makes it accessible from other devices on your local network
    # and not just from localhost.
    app.run(host='0.0.0.0', port=5000, debug=True)

