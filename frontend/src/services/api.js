import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Add request logging interceptor
axios.interceptors.request.use(request => {
  console.debug('API Request:', request.method?.toUpperCase(), request.url, request.data);
  return request;
});

// Add response logging interceptor
axios.interceptors.response.use(response => {
  console.debug('API Response:', response.status, response.data);
  return response;
});

export const getChatResponse = async (message) => {
  console.info('Sending message to /chat:', message);
  try {
    const response = await axios.post(`${API_URL}/chat`, { query: message });
    console.info('Received chat response:', response.data);
    return response.data.answer;
  } catch (error) {
    console.error('Chat API Error:', {
      message: error.message,
      response: error.response?.data,
      stack: error.stack
    });
    throw error;
  }
};

// New conversation management endpoints
export const fetchConversations = async (userId) => {
  console.info('Fetching conversations for user:', userId);
  try {
    const response = await axios.get(`${API_URL}/conversations?user_id=${userId}`);
    console.debug('Fetched conversations:', response.data.length, 'conversations');
    return response.data;
  } catch (error) {
    console.error('Fetch Conversations Error:', {
      status: error.response?.status,
      data: error.response?.data
    });
    throw error;
  }
};

export const createConversation = async (conversation) => {
  console.info('Creating conversation:', conversation.conversation_id);
  try {
    const response = await axios.post(`${API_URL}/conversations`, conversation);
    console.debug('Conversation created successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('Create Conversation Error:', {
      payload: conversation,
      error: error.response?.data
    });
    throw error;
  }
};

export const deleteConversation = async (conversationId) => {
  console.info('Deleting conversation:', conversationId);
  try {
    await axios.delete(`${API_URL}/conversations/${conversationId}`);
    console.debug('Successfully deleted conversation:', conversationId);
  } catch (error) {
    console.error('Delete Conversation Error:', {
      conversationId,
      status: error.response?.status,
      data: error.response?.data
    });
    throw error;
  }
};
