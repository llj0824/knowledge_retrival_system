## **Engineering Documentation: Knowledge Retrieval System Chatbot**

This document outlines the engineering approach for building the knowledge retrieval system chatbot, focusing on setting up the **Frontend** (React web app), **Backend** (FastAPI server with LLM and conversation routing), and **Infrastructure** for local development.

---

### **1. Frontend - React Web Application**

#### 1.1 **Overview**
The frontend will be a React web application that serves as the user interface for interacting with the chatbot. It will handle displaying the chat interface, managing user input, displaying chatbot responses, and interacting with the FastAPI backend.

#### 1.2 **Structure of the React App**

1. **Folder Structure**:
   ```plaintext
   src/
   ├── components/
   │   ├── ChatWindow.js           # Chat UI and message rendering
   │   ├── MessageInput.js         # Text input component
   │   ├── Header.js               # Application header (optional)
   ├── context/
   │   └── ChatContext.js          # State management for chat interactions
   ├── services/
   │   └── api.js                 # API calls to FastAPI backend
   ├── App.js                     # Main app component
   ├── index.js                   # Entry point to render React app
   └── styles/                     # CSS or SCSS files
   ```

2. **Libraries/Dependencies**:
   - **React**: `react`, `react-dom`
   - **React Router**: `react-router-dom` for handling routes (if needed)
   - **Axios**: `axios` for making HTTP requests to FastAPI backend

3. **Installation**:
   To set up the frontend locally, ensure Node.js is installed, then run:
   ```bash
   npx create-react-app knowledge-chatbot
   cd knowledge-chatbot
   npm install axios react-router-dom
   # Optionally for real-time chat:
   npm install socket.io-client
   ```

4. **App Component** (`App.js`):
   ```jsx
   import React, { useState, useEffect } from 'react';
   import MessageInput from './components/MessageInput';
   import ChatWindow from './components/ChatWindow';
   import { getChatResponse } from './services/api';

   const App = () => {
     const [messages, setMessages] = useState([]);
     
     // Function to handle user input and fetch bot response
     const sendMessage = async (message) => {
       setMessages([...messages, { sender: 'user', text: message }]);
       const botResponse = await getChatResponse(message);
       setMessages([...messages, { sender: 'user', text: message }, { sender: 'bot', text: botResponse }]);
     };

     return (
       <div className="chat-app">
         <ChatWindow messages={messages} />
         <MessageInput sendMessage={sendMessage} />
       </div>
     );
   };

   export default App;
   ```

5. **Message Input Component** (`MessageInput.js`):
   ```jsx
   import React, { useState } from 'react';

   const MessageInput = ({ sendMessage }) => {
     const [input, setInput] = useState("");

     const handleSend = () => {
       if (input.trim()) {
         sendMessage(input);
         setInput(""); // Clear input field
       }
     };

     return (
       <div className="message-input">
         <input
           type="text"
           value={input}
           onChange={(e) => setInput(e.target.value)}
           onKeyDown={(e) => e.key === "Enter" && handleSend()}
         />
         <button onClick={handleSend}>Send</button>
       </div>
     );
   };

   export default MessageInput;
   ```

6. **Chat Window Component** (`ChatWindow.js`):
   ```jsx
   const ChatWindow = ({ messages }) => {
     return (
       <div className="chat-window">
         {messages.map((message, index) => (
           <div key={index} className={`message ${message.sender}`}>
             <p>{message.text}</p>
           </div>
         ))}
       </div>
     );
   };

   export default ChatWindow;
   ```

7. **API Service** (`api.js`):
   ```javascript
   import axios from 'axios';

   const API_URL = 'http://localhost:8000/chat';

   export const getChatResponse = async (message) => {
     try {
       const response = await axios.post(API_URL, { query: message });
       return response.data.answer;
     } catch (error) {
       console.error("Error fetching chat response:", error);
       return "Sorry, something went wrong!";
     }
   };
   ```

---

### **2. Backend - FastAPI Server**

#### 2.1 **Overview**
The backend is built using **FastAPI**, which handles the incoming requests, routes the queries to the appropriate service (LLM, vector DB, or internet search), and returns the chatbot's response.

#### 2.2 **FastAPI Setup**

1. **Folder Structure**:
   ```plaintext
   backend/
   ├── main.py                    # FastAPI app and routes
   ├── models.py                  # Data models
   ├── services/
   │   ├── llm_service.py         # LLM integration
   │   ├── vector_db_service.py   # Vector DB integration
   │   ├── search_service.py      # Internet search integration
   └── requirements.txt           # Dependencies
   ```

2. **Dependencies**:
   ```bash
   pip install fastapi uvicorn openai pinecone-client
   pip install --upgrade faiss-cpu
   ```

3. **Main Application (FastAPI)** (`main.py`):
   ```python
   from fastapi import FastAPI
   from pydantic import BaseModel
   from services.llm_service import get_llm_response
   from services.vector_db_service import retrieve_from_vector_db
   from services.search_service import get_client_status_from_web

   app = FastAPI()

   class ChatRequest(BaseModel):
       query: str

   @app.post("/chat")
   async def chat(request: ChatRequest):
       query = request.query
       
       # Decision logic based on query type
       if "policy" in query:
           response = retrieve_from_vector_db(query)
       elif "client status" in query:
           response = get_client_status_from_web(query)
       else:
           response = get_llm_response(query)
       
       return {"answer": response}
   ```

4. **LLM Integration** (`llm_service.py`):
   ```python
   import openai

   openai.api_key = 'your-api-key'

   def get_llm_response(query: str) -> str:
       response = openai.Completion.create(
           engine="text-davinci-003",
           prompt=query,
           max_tokens=150
       )
       return response.choices[0].text.strip()
   ```

5. **Vector DB Integration** (`vector_db_service.py`):
   ```python
   import pinecone

   pinecone.init(api_key="your-pinecone-api-key", environment="us-west1-gcp")
   index = pinecone.Index("company-policy-documents")

   def retrieve_from_vector_db(query: str) -> str:
       result = index.query(query, top_k=1, include_values=True)
       return result['matches'][0]['metadata']['text'] if result['matches'] else "No relevant information found."
   ```

6. **Internet Search Integration** (`search_service.py`):
   ```python
   import requests

   def get_client_status_from_web(query: str) -> str:
       search_url = f"https://api.serpapi.com/search?q={query}&api_key=your-serpapi-api-key"
       response = requests.get(search_url).json()
       return response['organic_results'][0]['snippet'] if response['organic_results'] else "Client status not found."
   ```

---

### **3. Infrastructure - Running Locally**

#### 3.1 **Running React App Locally**

1. **Install Dependencies**:
   In the frontend directory, run:
   ```bash
   npm install
   ```

2. **Start the React App**:
   ```bash
   npm start
   ```

   This will launch the React application at `http://localhost:3000`.

#### 3.2 **Running FastAPI Server Locally**

1. **Install Dependencies**:
   In the backend directory, create a `requirements.txt` file and include the necessary packages:
   ```plaintext
   fastapi
   uvicorn
   openai
   pinecone-client
   faiss-cpu
   requests
   ```

   Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI Server**:
   Run the FastAPI app using `uvicorn`:
   ```bash
   uvicorn main:app --reload
   ```

   This will start the FastAPI server at `http://localhost:8000`.

#### 3.3 **Communication Between Frontend and Backend**

- The React app will make POST requests to the FastAPI server's `/chat` endpoint. Ensure the backend server is running before interacting with the frontend.
- Update the React API service to ensure the correct endpoint (`http://localhost:8000/chat`).

---

### **4. Next Steps**

1. **Testing**: 
   Test individual components and overall system for integration.
   
2. **

Deployment**: 
   Plan for deploying both the React app and FastAPI backend to cloud infrastructure (e.g., AWS, GCP, Heroku).

3. **Monitoring & Analytics**:
   Implement basic monitoring (e.g., logging, error tracking) for system performance and potential issues.

This document provides the necessary setup to begin working locally with React and FastAPI. Further steps will include expanding the system, fine-tuning the logic, and preparing for production deployment.