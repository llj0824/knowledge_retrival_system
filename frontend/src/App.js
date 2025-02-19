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
    const newMessage = { 
      sender: 'user', 
      content: message,
      timestamp: new Date().toISOString()
    };
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);
    
    try {
      const botResponse = await getChatResponse(message);
      console.info('[UI] Received bot response:', botResponse);
      
      const botMessage = { 
        sender: 'bot', 
        content: botResponse,
        timestamp: new Date().toISOString()
      };
      const finalMessages = [...updatedMessages, botMessage];
      setMessages(finalMessages);
      
      const conversationData = {
        user_id: userId,
        messages: finalMessages.map(m => ({
          content: m.content,
          sender: m.sender,
          timestamp: m.timestamp
        }))
      };

      if (!currentConversation) {
        console.info('[UI] Creating new conversation');
        const newConversation = await createConversation(conversationData);
        console.debug('[UI] New conversation created:', newConversation);
        setConversations([newConversation, ...conversations]);
        setCurrentConversation(newConversation);
      } else {
        console.info('[UI] Updating existing conversation:', currentConversation.conversation_id);
        const updatedConversation = await createConversation({
          ...conversationData,
          conversation_id: currentConversation.conversation_id
        });
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
        content: 'Sorry, something went wrong!',
        timestamp: new Date().toISOString()
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