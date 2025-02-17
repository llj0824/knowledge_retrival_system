### **Memory System Design for Chatbot**

#### **1. Database Selection**

Given the requirements for storing and managing text-based conversation logs, and considering the mild scalability needs, **MongoDB** is recommended due to its flexible NoSQL nature. 

**Key Advantages**:
- **Flexible Document Structure**: Conversations can be stored as documents, each containing the conversation ID, user ID, and message details.
- **Efficient Queries**: MongoDB provides easy query capabilities based on timestamps or metadata.
- **Horizontal Scalability**: While your traffic may be mild, MongoDB can scale horizontally as necessary.
- **Easy Data Management**: Deleting conversations (soft delete) is straightforward.


#### **2. Database Schema**

Assuming the use of **MongoDB**, the schema will be structured as follows:

- **Collection**: `conversations`
- **Fields**:
  - `conversation_id` (string): A timestamp-based unique identifier, e.g., `14:32 17/02/2025`.
  - `user_id` (string, optional): To track specific users.
  - `messages` (array of objects): A list of message objects, where each object includes:
    - `sender` (string): Either `"user"` or `"bot"`.
    - `message` (string): The content of the message.
    - `timestamp` (ISO 8601 string): The timestamp of the message.
  - `deleted` (boolean): A flag indicating whether the conversation has been deleted (soft delete).

**Example Document**:
```json
{
  "conversation_id": "14:32 17/02/2025",
  "user_id": "user123",
  "messages": [
    { "sender": "user", "message": "Hi, how are you?", "timestamp": "2025-02-17T14:32:01" },
    { "sender": "bot", "message": "I'm good, thanks for asking!", "timestamp": "2025-02-17T14:32:05" }
  ],
  "deleted": false
}
```

#### **3. Backend: Memory CRUD Operations**

**Endpoints**:
- **Create Conversation**: Store a new conversation when it begins.
- **Fetch All Conversations**: Retrieve all conversations for a specific user (or for all users for admin functionality).
- **Fetch Conversation**: Retrieve a specific conversation by its `conversation_id`.
- **Delete Conversation**: Soft delete a conversation by marking it as `deleted`.

**Example FastAPI Implementation**:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
import pytz

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client["chatbot"]
conversations_collection = db["conversations"]

class Message(BaseModel):
    sender: str
    message: str
    timestamp: str

class Conversation(BaseModel):
    user_id: str
    conversation_id: str
    messages: list[Message]

@app.post("/conversations/")
async def create_conversation(convo: Conversation):
    """Create a new conversation"""
    conversation = {
        "conversation_id": convo.conversation_id,
        "user_id": convo.user_id,
        "messages": convo.messages,
        "deleted": False
    }
    conversations_collection.insert_one(conversation)
    return {"message": "Conversation created"}

@app.get("/conversations/")
async def get_conversations(user_id: str):
    """Fetch all conversations for a user"""
    conversations = list(conversations_collection.find({"user_id": user_id, "deleted": False}))
    return conversations

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Fetch a specific conversation by ID"""
    conversation = conversations_collection.find_one({"conversation_id": conversation_id, "deleted": False})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation (soft delete)"""
    result = conversations_collection.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"deleted": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted"}
```

#### **4. Frontend: Conversation Management**

The frontend implements a hybrid design with a collapsible sidebar for conversation management alongside the main chat interface.

**UI Design**:
```
+[≡]-------------+--------------------------------+
|  Conversations |          Chat Window           |
|  [Collapsible] |                                |
| > Today 2:30PM |  [Messages appear here]        |
|   "How to..." |                                |
|   [Delete]     |                                |
|                |                                |
| > Yesterday    |                                |
|   "Tell me..." |                                |
|   [Delete]     |                                |
|                |                                |
| [+ New Chat]   |                                |
+----------------+  [Message Input]               |
                 +--------------------------------+
```

**Key Features**:
1. **Collapsible Sidebar**:
   - Toggle with hamburger menu (≡)
   - Shows list of past conversations
   - "New Chat" button at bottom
   - Each conversation shows timestamp and message preview
   - Delete button for each conversation

2. **Main Chat Window**:
   - Displays current conversation messages
   - Message input at bottom
   - Full-width when sidebar is collapsed

3. **Responsive Design**:
   - Sidebar becomes slide-out drawer on mobile
   - Optimized for both desktop and mobile views

**UI Flow**:
- Users can toggle the sidebar to view conversation history
- Selecting a conversation loads it in the main chat window
- New conversations can be started via the "New Chat" button
- Conversations can be deleted with individual delete buttons
- Mobile users access the conversation list through a drawer menu

The previous React example component should be updated to:

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ConversationList = ({ userId, onSelectConversation }) => {
  const [conversations, setConversations] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  useEffect(() => {
    const fetchConversations = async () => {
      const response = await axios.get(`/conversations?user_id=${userId}`);
      setConversations(response.data);
    };

    fetchConversations();
  }, [userId]);

  const deleteConversation = async (conversationId) => {
    await axios.delete(`/conversations/${conversationId}`);
    setConversations(conversations.filter(convo => convo.conversation_id !== conversationId));
  };

  return (
    <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
      <button className="toggle-sidebar" onClick={() => setSidebarOpen(!sidebarOpen)}>
        ≡
      </button>
      <div className="conversations-list">
        {conversations.map(convo => (
          <div key={convo.conversation_id} className="conversation-item">
            <div onClick={() => onSelectConversation(convo)}>
              <span className="timestamp">{convo.conversation_id}</span>
              <span className="preview">
                {convo.messages[0]?.message.substring(0, 30)}...
              </span>
            </div>
            <button 
              className="delete-button"
              onClick={() => deleteConversation(convo.conversation_id)}
            >
              Delete
            </button>
          </div>
        ))}
      </div>
      <button className="new-chat-button">New Chat</button>
    </div>
  );
};

export default ConversationList;
```

#### **5. MongoDB Setup and Installation**

If you're running MongoDB locally, follow the instructions for your operating system:

**Windows**:
- Download MongoDB from [MongoDB's website](https://www.mongodb.com/try/download/community) and install it as a service.

**macOS**:
- Install MongoDB via Homebrew:
  ```bash
  brew tap mongodb/brew
  brew install mongodb-community@6.0
  brew services start mongodb/brew/mongodb-community
  ```

**Linux**:
- For Ubuntu/Debian:
  ```bash
  sudo apt update
  sudo apt install -y mongodb
  sudo systemctl start mongodb
  sudo systemctl enable mongodb
  ```

### **Conclusion**

This system design ensures the easy storage, retrieval, and management of conversation logs, while providing flexibility for future scaling needs. The use of MongoDB ensures smooth data handling with a simple CRUD API, and the frontend enables easy interaction for users and administrators.

---

This version presents the key points more concisely and clearly defines the steps, making it easier for engineers to implement.