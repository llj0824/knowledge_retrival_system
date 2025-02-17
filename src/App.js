import React, { useState } from 'react';
import MessageInput from './components/MessageInput';
import ChatWindow from './components/ChatWindow';
import Header from './components/Header';
import { getChatResponse } from './services/api';
import './styles/App.css';

const App = () => {
  const [messages, setMessages] = useState([]);
  
  const sendMessage = async (message) => {
    // Add user message
    const updatedMessages = [...messages, { sender: 'user', text: message }];
    setMessages(updatedMessages);
    
    try {
      // Get bot response
      const botResponse = await getChatResponse(message);
      setMessages([...updatedMessages, { sender: 'bot', text: botResponse }]);
    } catch (error) {
      setMessages([...updatedMessages, { sender: 'bot', text: 'Sorry, something went wrong!' }]);
    }
  };

  return (
    <div className="app">
      <Header />
      <div className="chat-container">
        <ChatWindow messages={messages} />
        <MessageInput sendMessage={sendMessage} />
      </div>
    </div>
  );
};

export default App;