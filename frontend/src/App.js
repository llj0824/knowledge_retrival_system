import React, { useState, useEffect } from 'react';
import MessageInput from './components/MessageInput';
import ChatWindow from './components/ChatWindow';
import Header from './components/Header';
import ConversationList from './components/ConversationList';
import { 
  getChatResponse, 
  fetchConversations, 
  createConversation, 
  deleteConversation 
} from './services/api';
import './styles/App.css';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);
  const userId = "test-user"; // In a real app, this would come from auth
  
  // Load conversations on mount
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const data = await fetchConversations(userId);
        setConversations(data);
      } catch (error) {
        console.error("Failed to load conversations:", error);
      } finally {
        setLoading(false);
      }
    };

    loadConversations();
  }, [userId]);

  const sendMessage = async (message) => {
    const newMessage = { sender: 'user', text: message };
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);
    
    try {
      const botResponse = await getChatResponse(message);
      const botMessage = { sender: 'bot', text: botResponse };
      const finalMessages = [...updatedMessages, botMessage];
      setMessages(finalMessages);
      
      // Save conversation
      if (!currentConversation) {
        // Create new conversation
        const newConversation = {
          user_id: userId,
          conversation_id: new Date().toLocaleString(),
          messages: finalMessages
        };
        
        await createConversation(newConversation);
        setConversations([newConversation, ...conversations]);
        setCurrentConversation(newConversation);
      } else {
        // Update existing conversation
        const updatedConversation = {
          ...currentConversation,
          messages: finalMessages
        };
        await createConversation(updatedConversation); // Use PUT in a real implementation
        setConversations(conversations.map(c => 
          c.conversation_id === currentConversation.conversation_id 
            ? updatedConversation 
            : c
        ));
        setCurrentConversation(updatedConversation);
      }
    } catch (error) {
      setMessages([...updatedMessages, { 
        sender: 'bot', 
        text: 'Sorry, something went wrong!' 
      }]);
    }
  };

  const handleSelectConversation = (conversation) => {
    setCurrentConversation(conversation);
    setMessages(conversation.messages);
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await deleteConversation(conversationId);
      setConversations(conversations.filter(c => c.conversation_id !== conversationId));
      if (currentConversation?.conversation_id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (error) {
      console.error("Failed to delete conversation:", error);
      // Show error message to user
    }
  };

  const handleNewChat = () => {
    setCurrentConversation(null);
    setMessages([]);
  };

  return (
    <div className="app">
      <Header />
      <div className="main-container">
        <ConversationList 
          conversations={conversations}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
          onNewChat={handleNewChat}
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
        />
        <div className={`chat-container ${sidebarOpen ? 'with-sidebar' : ''}`}>
          <ChatWindow messages={messages} />
          <MessageInput sendMessage={sendMessage} />
        </div>
      </div>
    </div>
  );
};

export default App;