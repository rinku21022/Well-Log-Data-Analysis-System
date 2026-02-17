import axios from 'axios';

// Support multiple deployment env var names and fall back to a relative API path.
// Prefer CRA-style REACT_APP_API_URL, then Vite-style VITE_API_BASE_URL, then
// check for a runtime global (window.VITE_API_BASE_URL) for platforms that
// inject client envs at runtime, then fall back to '/api'.
const runtimeGlobal = (typeof window !== 'undefined') ? (window.REACT_APP_API_URL || window.VITE_API_BASE_URL || (window.__ENV && (window.__ENV.REACT_APP_API_URL || window.__ENV.VITE_API_BASE_URL))) : undefined;

// Final fallback order:
// 1. process.env.REACT_APP_API_URL (build-time CRA)
// 2. process.env.VITE_API_BASE_URL (build-time Vite)
// 3. runtime globals (window.REACT_APP_API_URL / window.VITE_API_BASE_URL / window.__ENV)
// 4. relative '/api' (same-origin) - works with Vercel rewrites
const API_BASE_URL = process.env.REACT_APP_API_URL || process.env.VITE_API_BASE_URL || runtimeGlobal || '/api';

console.log('API_BASE_URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getFiles = async () => {
  const response = await api.get('/files');
  return response.data;
};

export const getFile = async (fileId) => {
  const response = await api.get(`/file/${fileId}`);
  return response.data;
};

export const getCurves = async (fileId) => {
  const response = await api.get(`/curves/${fileId}`);
  return response.data;
};

export const getVisualizationData = async (fileId, curves, startDepth, endDepth) => {
  const response = await api.post('/visualize', {
    file_id: fileId,
    curves: curves,
    start_depth: startDepth,
    end_depth: endDepth,
  });
  return response.data;
};

export const getInterpretation = async (fileId, curves, startDepth, endDepth) => {
  const response = await api.post('/interpret', {
    file_id: fileId,
    curves: curves,
    start_depth: startDepth,
    end_depth: endDepth,
  });
  return response.data;
};

export const getInterpretations = async (fileId) => {
  const response = await api.get(`/interpretations/${fileId}`);
  return response.data;
};

export const chatWithAI = async (fileId, message, conversationHistory) => {
  const response = await api.post('/chat', {
    file_id: fileId,
    message: message,
    conversation_history: conversationHistory,
  });
  return response.data;
};

export const deleteFile = async (fileId) => {
  const response = await api.delete(`/file/${fileId}`);
  return response.data;
};

export default api;
