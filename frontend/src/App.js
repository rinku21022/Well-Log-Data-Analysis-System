import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Tab,
  Tabs,
  Paper,
} from '@mui/material';
import OilBarrelIcon from '@mui/icons-material/OilBarrel';

import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import Visualization from './components/Visualization';
import AIInterpretation from './components/AIInterpretation';
import Chatbot from './components/Chatbot';

import { getFiles } from './services/api';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const data = await getFiles();
      setFiles(data.files);
    } catch (error) {
      console.error('Error loading files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = () => {
    loadFiles();
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setTabValue(1); // Switch to visualization tab
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <div className="App">
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <OilBarrelIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Well-Log Data Analysis System
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab label="Upload & Files" />
            <Tab label="Visualization" disabled={!selectedFile} />
            <Tab label="AI Interpretation" disabled={!selectedFile} />
            <Tab label="Chatbot" disabled={!selectedFile} />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <FileUpload onUploadSuccess={handleFileUpload} />
            <Box sx={{ mt: 4 }}>
              <FileList
                files={files}
                onFileSelect={handleFileSelect}
                onFileDelete={loadFiles}
                loading={loading}
              />
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {selectedFile && (
              <Visualization file={selectedFile} />
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            {selectedFile && (
              <AIInterpretation file={selectedFile} />
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            {selectedFile && (
              <Chatbot file={selectedFile} />
            )}
          </TabPanel>
        </Paper>

        {selectedFile && (
          <Paper elevation={2} sx={{ mt: 2, p: 2, backgroundColor: '#e3f2fd' }}>
            <Typography variant="subtitle2" color="primary">
              <strong>Selected File:</strong> {selectedFile.filename}
            </Typography>
            <Typography variant="body2">
              Well: {selectedFile.well_name || 'N/A'} | 
              Depth: {selectedFile.start_depth} - {selectedFile.stop_depth} {selectedFile.depth_unit}
            </Typography>
          </Paper>
        )}
      </Container>
    </div>
  );
}

export default App;
