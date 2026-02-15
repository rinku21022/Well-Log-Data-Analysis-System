import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadFile } from '../services/api';

function FileUpload({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.las')) {
      setError('Please upload a .las file');
      return;
    }

    setUploading(true);
    setError(null);
    setMessage(null);
    setProgress(30);

    try {
      setProgress(60);
      const response = await uploadFile(file);
      setProgress(100);
      setMessage(`File "${file.name}" uploaded successfully!`);
      
      if (onUploadSuccess) {
        onUploadSuccess(response.file);
      }

      // Reset after 3 seconds
      setTimeout(() => {
        setMessage(null);
        setProgress(0);
      }, 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Error uploading file');
      setProgress(0);
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/las': ['.las', '.LAS'],
    },
    multiple: false,
  });

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Upload LAS File
      </Typography>
      
      <Paper
        {...getRootProps()}
        elevation={isDragActive ? 6 : 2}
        sx={{
          p: 4,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.400',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          textAlign: 'center',
          transition: 'all 0.3s',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        
        {isDragActive ? (
          <Typography variant="h6">Drop the LAS file here...</Typography>
        ) : (
          <>
            <Typography variant="h6" gutterBottom>
              Drag & drop a LAS file here
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              or
            </Typography>
            <Button variant="contained" component="span">
              Browse Files
            </Button>
          </>
        )}
      </Paper>

      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Uploading and processing...
          </Typography>
        </Box>
      )}

      {message && (
        <Alert severity="success" sx={{ mt: 2 }}>
          {message}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
}

export default FileUpload;
