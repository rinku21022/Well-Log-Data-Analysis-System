import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  Avatar,
  CircularProgress,
  Divider,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import { chatWithAI } from '../services/api';

function Chatbot({ file }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello! I'm your AI assistant for analyzing well-log data. I have access to the data from "${file.filename}". Feel free to ask me questions about the well, the curves, depth ranges, or anything else related to this data.`,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to chat
    const newMessages = [
      ...messages,
      {
        role: 'user',
        content: userMessage,
      },
    ];
    setMessages(newMessages);
    setLoading(true);

    try {
      // Prepare conversation history for API
      const conversationHistory = newMessages.slice(1).map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await chatWithAI(file.id, userMessage, conversationHistory);

      // Add AI response to chat
      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: response.response,
        },
      ]);
    } catch (error) {
      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: `Sorry, I encountered an error: ${error.response?.data?.error || error.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        <SmartToyIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
        AI Chatbot
      </Typography>

      <Paper
        elevation={3}
        sx={{
          height: '600px',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* Messages Area */}
        <Box
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            p: 2,
            backgroundColor: '#f5f5f5',
          }}
        >
          <List>
            {messages.map((message, index) => (
              <ListItem
                key={index}
                sx={{
                  flexDirection: 'column',
                  alignItems: message.role === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2,
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    maxWidth: '80%',
                    flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                      width: 35,
                      height: 35,
                      mx: 1,
                    }}
                  >
                    {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
                  </Avatar>

                  <Paper
                    elevation={2}
                    sx={{
                      p: 2,
                      backgroundColor: message.role === 'user' ? '#e3f2fd' : 'white',
                      borderRadius: 2,
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
                    >
                      {message.content}
                    </Typography>
                  </Paper>
                </Box>
              </ListItem>
            ))}

            {loading && (
              <ListItem sx={{ justifyContent: 'flex-start' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar
                    sx={{
                      bgcolor: 'secondary.main',
                      width: 35,
                      height: 35,
                      mr: 1,
                    }}
                  >
                    <SmartToyIcon />
                  </Avatar>
                  <Paper elevation={2} sx={{ p: 2 }}>
                    <CircularProgress size={20} />
                  </Paper>
                </Box>
              </ListItem>
            )}

            <div ref={messagesEndRef} />
          </List>
        </Box>

        <Divider />

        {/* Input Area */}
        <Box sx={{ p: 2, backgroundColor: 'white' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder="Ask a question about your well-log data..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              variant="outlined"
            />
            <Button
              variant="contained"
              onClick={handleSend}
              disabled={!input.trim() || loading}
              sx={{ minWidth: '100px' }}
              endIcon={<SendIcon />}
            >
              Send
            </Button>
          </Box>
          
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Press Enter to send, Shift+Enter for new line
          </Typography>
        </Box>
      </Paper>

      <Paper elevation={1} sx={{ mt: 2, p: 2, backgroundColor: '#fff3e0' }}>
        <Typography variant="subtitle2" gutterBottom>
          <strong>Example Questions:</strong>
        </Typography>
        <Typography variant="body2">
          • What curves are available in this file?
          <br />
          • What is the depth range of the well?
          <br />
          • Can you explain what the GR curve indicates?
          <br />
          • What are the average values for the porosity curve?
          <br />
          • Are there any anomalies in the data?
        </Typography>
      </Paper>
    </Box>
  );
}

export default Chatbot;
