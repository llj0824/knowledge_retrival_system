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
    console.info('[UI] Sending message:', message);
    const newMessage = { sender: 'user', text: message };
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);
    
    try {
      const botResponse = await getChatResponse(message);
      console.info('[UI] Received bot response:', botResponse);
      
      const botMessage = { sender: 'bot', text: botResponse };
      const finalMessages = [...updatedMessages, botMessage];
      setMessages(finalMessages);
      
      if (!currentConversation) {
        console.info('[UI] Creating new conversation');
        const newConversation = {
          user_id: userId,
          conversation_id: new Date().toLocaleString(),
          messages: finalMessages
        };
        
        await createConversation(newConversation);
        console.debug('[UI] New conversation created:', newConversation);
        setConversations([newConversation, ...conversations]);
        setCurrentConversation(newConversation);
      } else {
        console.info('[UI] Updating existing conversation:', currentConversation.conversation_id);
        const updatedConversation = {
          ...currentConversation,
          messages: finalMessages
        };
        await createConversation(updatedConversation);
        console.debug('[UI] Conversation updated:', updatedConversation);
        setConversations(conversations.map(c => 
          c.conversation_id === currentConversation.conversation_id 
            ? updatedConversation 
            : c
        ));
        setCurrentConversation(updatedConversation);
      }
    } catch (error) {
      console.error('[UI] Message handling failed:', error);
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
    console.info('[UI] Deleting conversation:', conversationId);
    try {
      await deleteConversation(conversationId);
      console.debug('[UI] Deleted conversation:', conversationId);
      setConversations(conversations.filter(c => c.conversation_id !== conversationId));
      if (currentConversation?.conversation_id === conversationId) {
        console.debug('[UI] Clearing current conversation after deletion');
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('[UI] Delete conversation failed:', {
        error,
        conversationId
      });
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