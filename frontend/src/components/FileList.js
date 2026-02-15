import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  IconButton,
  Paper,
  Chip,
  CircularProgress,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import DescriptionIcon from '@mui/icons-material/Description';
import { deleteFile } from '../services/api';

function FileList({ files, onFileSelect, onFileDelete, loading }) {
  const handleDelete = async (fileId, filename) => {
    if (window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      try {
        await deleteFile(fileId);
        if (onFileDelete) {
          onFileDelete();
        }
      } catch (error) {
        alert('Error deleting file: ' + (error.response?.data?.error || error.message));
      }
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!files || files.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No files uploaded yet. Upload a LAS file to get started.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Uploaded Files
      </Typography>
      
      <Paper elevation={2}>
        <List>
          {files.map((file, index) => (
            <ListItem
              key={file.id}
              divider={index < files.length - 1}
              secondaryAction={
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => handleDelete(file.id, file.filename)}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              }
            >
              <ListItemButton onClick={() => onFileSelect(file)}>
                <DescriptionIcon sx={{ mr: 2, color: 'primary.main' }} />
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">
                        {file.filename}
                      </Typography>
                      <Chip
                        label={`${file.available_curves?.length || 0} curves`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography component="span" variant="body2">
                        {file.well_name && `Well: ${file.well_name} • `}
                        Depth: {file.start_depth?.toFixed(2)} - {file.stop_depth?.toFixed(2)} {file.depth_unit}
                      </Typography>
                      <br />
                      <Typography component="span" variant="caption" color="text.secondary">
                        Uploaded: {new Date(file.upload_date).toLocaleString()}
                      </Typography>
                    </>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
}

export default FileList;
