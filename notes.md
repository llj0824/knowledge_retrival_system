## 2025/2/17

""" plaintext
When the user runs start.sh, it should start both the backend and frontend. The backend is a FastAPI server using main.py, and the frontend is a React app. The start.sh script probably runs the backend server with uvicorn and the frontend with npm start. So the first part is about the execution order of these files.
Next, when a message is sent, the frontend's App.js uses the sendMessage function, which calls getChatResponse from api.js. That sends a POST request to the backend's /chat endpoint. The backend's main.py handles this request, decides the context, and routes it to the appropriate service (LLM, vector DB, or web search). The LLM service in llm_service.py uses OpenAI to generate a response. But wait, in the initial code, the LLM service wasn't handling conversation history. Oh right, the user's last question is about how the conversation history is maintained so the LLM has context.
Looking at the frontend's App.js, the messages are stored in state with useState. Each time a message is sent, it's added to the messages array. However, the current sendMessage function only sends the current message to the backend, not the history. That means the backend doesn't receive past messages, so the LLM doesn't have context. Oh, that's a problem! The initial implementation doesn't pass the conversation history to the backend, so each message is treated in isolation.
"""


sequenceDiagram
    participant User
    participant start.sh
    participant Backend (FastAPI)
    participant Frontend (React)
    
    User->>start.sh: ./start.sh
    start.sh->>Backend: uvicorn main:app --reload
    Backend->>main.py: Execute
    main.py->>vector_db_service.py: initialize_db()
    start.sh->>Frontend: npm start
    Frontend->>App.js: Mount components
    App.js->>api.js: Initialize API service

sequenceDiagram
    participant User
    participant MessageInput.js
    participant App.js
    participant api.js
    participant Backend (main.py)
    participant llm_service.py
    participant vector_db_service.py
    
    User->>MessageInput.js: Types message
    MessageInput.js->>App.js: sendMessage()
    App.js->>api.js: getChatResponse(message)
    api.js->>Backend: POST /chat {query: message}
    Backend->>main.py: chat()
    main.py->>vector_db_service.py: retrieve_from_vector_db() if policy
    main.py->>llm_service.py: get_llm_response() if general
    llm_service.py->>OpenAI: API Call
    OpenAI-->>llm_service.py: Response
    llm_service.py-->>main.py: Return text
    main.py-->>api.js: JSON response
    api.js-->>App.js: Return answer
    App.js->>ChatWindow.js: Update messages