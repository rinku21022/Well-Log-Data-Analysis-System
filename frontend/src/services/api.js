import axios from 'axios';

// Get backend URL - MUST be set as environment variable
const BACKEND_URL = process.env.REACT_APP_API_URL;

console.log('=== API Configuration ===');
console.log('REACT_APP_API_URL:', BACKEND_URL);

if (!BACKEND_URL) {
  console.error('❌ CRITICAL: REACT_APP_API_URL environment variable is NOT SET');
  console.error('Please set REACT_APP_API_URL in Vercel environment variables');
  console.error('Example: https://your-railway-backend.up.railway.app');
}

// All API calls will use the Backend URL directly
const api = axios.create({
  baseURL: BACKEND_URL || 'http://localhost:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Debug interceptor
api.interceptors.request.use(request => {
  console.log('REQUEST:', request.method.toUpperCase(), request.url);
  return request;
});

api.interceptors.response.use(
  response => {
    console.log('RESPONSE:', response.status, response.config.url);
    return response;
  },
  error => {
    console.error('API ERROR:', {
      url: error.config?.url,
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  console.log('Uploading file:', file.name, 'to', `${BACKEND_URL}/api/upload`);
  
  const response = await api.post('/api/upload', formData);
  return response.data;
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
