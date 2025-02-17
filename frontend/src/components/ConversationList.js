import React from 'react';
import '../styles/Sidebar.css';

const ConversationList = ({ 
  conversations, 
  onSelectConversation, 
  onDeleteConversation,
  onNewChat,
  isOpen,
  onToggle,
  loading = false
}) => {
  return (
    <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <button className="toggle-sidebar" onClick={onToggle}>
        ≡
      </button>
      <div className="conversations-list">
        {loading ? (
          <div className="loading">Loading conversations...</div>
        ) : conversations.length === 0 ? (
          <div className="no-conversations">No conversations yet</div>
        ) : (
          conversations.map(convo => (
            <div key={convo.conversation_id} className="conversation-item">
              <div 
                className="conversation-preview"
                onClick={() => onSelectConversation(convo)}
              >
                <span className="timestamp">{convo.conversation_id}</span>
                <span className="preview">
                  {convo.messages[0]?.text.substring(0, 30)}...
                </span>
              </div>
              <button 
                className="delete-button"
                onClick={() => onDeleteConversation(convo.conversation_id)}
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
      <button className="new-chat-button" onClick={onNewChat}>
        New Chat
      </button>
    </div>
  );
};

export default ConversationList; 