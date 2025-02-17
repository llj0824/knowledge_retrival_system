import axios from 'axios';

const API_URL = 'http://localhost:8000/chat';

export const getChatResponse = async (message) => {
  try {
    const response = await axios.post(API_URL, { query: message });
    return response.data.answer;
  } catch (error) {
    console.error("Error fetching chat response:", error);
    throw error;
  }
};
