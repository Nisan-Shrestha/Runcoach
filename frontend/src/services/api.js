import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const chatAPI = {
  sendMessage: async (message, userProfile = null) => {
    const response = await api.post("/chat", {
      message,
      user_profile: userProfile,
    });
    return response.data;
  },

  resetChat: async () => {
    const response = await api.post("/reset");
    return response.data;
  },
};

export const profileAPI = {
  saveProfile: async (profile) => {
    const response = await api.post("/profile", profile);
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get("/profile");
    return response.data;
  },
};

export const quickQuestionsAPI = {
  getQuestions: async () => {
    const response = await api.get("/quick-questions");
    return response.data;
  },
};

export default api;
