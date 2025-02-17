import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const getChatResponse = async (message) => {
  try {
    const response = await axios.post(`${API_URL}/chat`, { query: message });
    return response.data.answer;
  } catch (error) {
    console.error("Error fetching chat response:", error);
    throw error;
  }
};

// New conversation management endpoints
export const fetchConversations = async (userId) => {
  try {
    const response = await axios.get(`${API_URL}/conversations?user_id=${userId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching conversations:", error);
    throw error;
  }
};

export const createConversation = async (conversation) => {
  try {
    const response = await axios.post(`${API_URL}/conversations`, conversation);
    return response.data;
  } catch (error) {
    console.error("Error creating conversation:", error);
    throw error;
  }
};

export const deleteConversation = async (conversationId) => {
  try {
    await axios.delete(`${API_URL}/conversations/${conversationId}`);
  } catch (error) {
    console.error("Error deleting conversation:", error);
    throw error;
  }
};
