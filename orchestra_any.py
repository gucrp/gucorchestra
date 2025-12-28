from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import requests, json

app = Flask(__name__)
CORS(app) # Enable CORS for all routes and all origins (*)

filename = "log_" + datetime.now().strftime("%Y-%m-%d") + ".txt"
with open(filename, 'a') as file:
    pass

# Configuration for ANYTHINGLLM
API_BASE_URL = "http://127.0.0.1:3001/api"
API_KEY = "S6X81SX-5SFM0EA-GAB20E0-WJ3VXPQ"
WORKSPACE_SLUG = "mainworkspace"


headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}

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
    
    #ANYLLM payload para criar thread
    new_thread_payload = {
        "userId": userid,
        "name": f"{userid}.{firstname}_{lastname}",
        "slug": f"mdl_usr_{userid}"
    }
    
    #endpoint para new thread
    endpointT = f"{API_BASE_URL}/v1/workspace/{WORKSPACE_SLUG}/thread/new"
    
    #ANYLLM create thread (cria thread para o usuário. Se já existe retorna erro mas continua o código)
    try:
        responset = requests.post(endpointT, headers=headers, data=json.dumps(new_thread_payload))
        responset.raise_for_status()
        responseThread = responset.json()
        #print("AI Response:", response['textResponse']) # The key might be different depending on the exact API version
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    print(json.dumps(responseThread, indent=4))
    
    #ANYLLM payload para mensagem
    msg_payload = {
        "message": user_message,
        "mode": "chat",
        "reset": False,
        "sessionId": f"mdl_usr_{userid}"
    }

    #endpoint para msg
    endpoint = f"{API_BASE_URL}/v1/workspace/{WORKSPACE_SLUG}/thread/mdl_usr_{userid}/chat"

    #ANYLLM send msg para thread
    try:
        response1 = requests.post(endpoint, headers=headers, data=json.dumps(msg_payload))
        response1.raise_for_status()
        response = response1.json()
        #print("AI Response:", response['textResponse']) # The key might be different depending on the exact API version
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
  
    # --- Show data in terminal ---
    #Moodle data
    print(f"\nCourse data: {coursedata}")
    print(f"Moodle User ID: {userid}")
    print(f"User Full Name: {firstname} {lastname}")
    print(f"Moodle Course ID: {courseid}")
    print(f"Course Name: {coursename}")
    print(f"User Message: {user_message}")
    
    #AnythingLLM Data
    # --- Core Metadata ---
    print(f"\nSession ID: mdl_usr_{userid}")
    print(f"Response ID: {response['id']}")
    print(f"Type: {response['type']}")
    print(f"Session Closed: {response['close']}")
    print(f"Error Status: {response['error']}")
    print(f"Chat ID: {response['chatId']}")

# --- The Actual Message ---
    #print(f"\nAI Response: {response['textResponse']}")

# --- Metrics (Continuing your pattern) ---
    print(f"\nDuration (s): {response['metrics']['duration']}")
    print(f"Prompt Tokens: {response['metrics']['prompt_tokens']}")
    print(f"Output Tokens: {response['metrics']['completion_tokens']}")
    print(f"Total Tokens: {response['metrics']['total_tokens']}")
    print(f"Tokens per Second: {response['metrics']['outputTps']:.2f}")

# --- Sources (Looping through the list of citations) ---
    print("\n--- SOURCES USED ---")
    for i, source in enumerate(response['sources'], 1):
        print(f"\nSource #{i}:")
        print(f"  Title: {source['title']}")
        print(f"  Score: {source['score']}")
        print(f"  Re-rank Score: {source['rerank_score']}")
        print(f"  Distance: {source['_distance']}")
        print(f"  File Path: {source['url']}")
        print(f"  Description: {source['description']}")
        print(f"  Word Count: {source['wordCount']}")
        print(f"  Token Estimate: {source['token_count_estimate']}")
        print(f"  Published: {source['published']}")
        # Optionally print the first 50 chars of the text snippet
        print(f"  Snippet Preview: {source['text'][:50]}...")
    
    # --- Criar e incrementar arquivo de LOG, uma mesnagem por linha ---
    
    with open(f"{filename}", 'a', encoding="utf-8") as f:
    # Using parentheses allows automatic line joining without backslashes
        print(
        f"{timestamp};{userid};{firstname};{lastname};"
        f"{response['metrics']['prompt_tokens']};"
        f"{response['metrics']['completion_tokens']};"
        f"{response['metrics']['total_tokens']};"
        f"{response['metrics']['outputTps']};"
        f"{response['metrics']['duration']};"
        f"{user_message};"
        f"{response['textResponse'].replace(';', ',').replace('\r', '\\n').replace('\n', '\\n')}", 
        file=f
    )

    # montando a resposta:
    bot_reply = (
        #f"UID: {userid} - Instance: {instance_id} "
        f"({timestamp})"
        f"\n{response['textResponse']}"
     
    )

    # --- End Chatbot Logic ---

    # Return the response as JSON
    return jsonify({"reply": bot_reply})

# Optional: A simple root endpoint to check if the API is running

@app.route('/', methods=['GET'])
def index():
    return "Python Chatbot API is running!"

if __name__ == '__main__':
    # For local development, host='0.0.0.0' makes it accessible from other devices on your local network
    # and not just from localhost.
    app.run(host='127.0.0.1', port=5000, debug=True)

