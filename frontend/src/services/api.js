import axios from 'axios';

// Support multiple deployment env var names and fall back to a relative API path.
const runtimeGlobal = (typeof window !== 'undefined') ? (window.REACT_APP_API_URL || window.VITE_API_BASE_URL) : undefined;

// Determine API base URL
let API_BASE_URL = process.env.REACT_APP_API_URL || process.env.VITE_API_BASE_URL || runtimeGlobal;

// Log for debugging
console.log('Environment check:');
console.log('process.env.REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
console.log('process.env.VITE_API_BASE_URL:', process.env.VITE_API_BASE_URL);
console.log('Final API_BASE_URL:', API_BASE_URL);

// If no explicit backend URL, warn the user
if (!API_BASE_URL) {
  console.warn('⚠️ No backend URL configured. Requests will fail. Set REACT_APP_API_URL environment variable.');
  API_BASE_URL = 'http://localhost:5000'; // Fallback for development
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for debugging
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    console.log('Uploading file to:', `${API_BASE_URL}/api/upload`);
    
    const response = await api.post('/api/upload', formData);
    
    return response.data;
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
};

export const getFiles = async () => {
  const response = await api.get('/api/files');
  return response.data;
};

export const getFile = async (fileId) => {
  const response = await api.get(`/api/file/${fileId}`);
  return response.data;
};

export const getCurves = async (fileId) => {
  const response = await api.get(`/api/curves/${fileId}`);
  return response.data;
};

export const getVisualizationData = async (fileId, curves, startDepth, endDepth) => {
  const response = await api.post('/api/visualize', {
    file_id: fileId,
    curves: curves,
    start_depth: startDepth,
    end_depth: endDepth,
  });
  return response.data;
};

export const getInterpretation = async (fileId, curves, startDepth, endDepth) => {
  const response = await api.post('/api/interpret', {
    file_id: fileId,
    curves: curves,
    start_depth: startDepth,
    end_depth: endDepth,
  });
  return response.data;
};

export const getInterpretations = async (fileId) => {
  const response = await api.get(`/api/interpretations/${fileId}`);
  return response.data;
};

export const chatWithAI = async (fileId, message, conversationHistory) => {
  const response = await api.post('/api/chat', {
    file_id: fileId,
    message: message,
    conversation_history: conversationHistory,
  });
  return response.data;
};

export const deleteFile = async (fileId) => {
  const response = await api.delete(`/api/file/${fileId}`);
  return response.data;
};

export default api;
