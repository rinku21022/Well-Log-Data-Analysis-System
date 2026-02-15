import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  ListItemText,
  OutlinedInput,
  TextField,
  Button,
  Paper,
  Grid,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider,
  Chip,
} from '@mui/material';
import PsychologyIcon from '@mui/icons-material/Psychology';
import HistoryIcon from '@mui/icons-material/History';
import { getCurves, getInterpretation, getInterpretations } from '../services/api';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

function AIInterpretation({ file }) {
  const [curves, setCurves] = useState([]);
  const [selectedCurves, setSelectedCurves] = useState([]);
  const [startDepth, setStartDepth] = useState(file.start_depth);
  const [endDepth, setEndDepth] = useState(file.stop_depth);
  const [interpretation, setInterpretation] = useState(null);
  const [pastInterpretations, setPastInterpretations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCurves();
    loadPastInterpretations();
  }, [file.id]);

  const loadCurves = async () => {
    try {
      const data = await getCurves(file.id);
      setCurves(data.curves);
      
      // Auto-select all curves
      if (data.curves.length > 0) {
        setSelectedCurves(data.curves.map(c => c.curve_name));
      }
    } catch (err) {
      setError('Error loading curves: ' + (err.response?.data?.error || err.message));
    }
  };

  const loadPastInterpretations = async () => {
    try {
      const data = await getInterpretations(file.id);
      setPastInterpretations(data.interpretations);
    } catch (err) {
      console.error('Error loading past interpretations:', err);
    }
  };

  const handleCurveChange = (event) => {
    const value = event.target.value;
    setSelectedCurves(typeof value === 'string' ? value.split(',') : value);
  };

  const handleInterpret = async () => {
    if (selectedCurves.length === 0) {
      setError('Please select at least one curve');
      return;
    }

    setLoading(true);
    setError(null);
    setInterpretation(null);

    try {
      const data = await getInterpretation(
        file.id,
        selectedCurves,
        startDepth,
        endDepth
      );

      setInterpretation(data.interpretation);
      loadPastInterpretations(); // Reload to include new interpretation
    } catch (err) {
      setError('Error generating interpretation: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const formatInterpretation = (text) => {
    return text.split('\n').map((line, index) => (
      <Typography
        key={index}
        variant="body1"
        paragraph
        sx={{ whiteSpace: 'pre-wrap' }}
      >
        {line}
      </Typography>
    ));
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        <PsychologyIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
        AI-Assisted Interpretation
      </Typography>

      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Select Curves</InputLabel>
              <Select
                multiple
                value={selectedCurves}
                onChange={handleCurveChange}
                input={<OutlinedInput label="Select Curves" />}
                renderValue={(selected) => selected.join(', ')}
                MenuProps={MenuProps}
              >
                {curves.map((curve) => (
                  <MenuItem key={curve.curve_name} value={curve.curve_name}>
                    <Checkbox checked={selectedCurves.indexOf(curve.curve_name) > -1} />
                    <ListItemText
                      primary={`${curve.curve_name} (${curve.curve_unit})`}
                      secondary={curve.curve_description}
                    />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Start Depth"
              type="number"
              value={startDepth}
              onChange={(e) => setStartDepth(parseFloat(e.target.value))}
              InputProps={{
                inputProps: {
                  min: file.start_depth,
                  max: file.stop_depth,
                  step: file.step || 0.1,
                },
              }}
            />
          </Grid>

          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="End Depth"
              type="number"
              value={endDepth}
              onChange={(e) => setEndDepth(parseFloat(e.target.value))}
              InputProps={{
                inputProps: {
                  min: file.start_depth,
                  max: file.stop_depth,
                  step: file.step || 0.1,
                },
              }}
            />
          </Grid>

          <Grid item xs={12}>
            <Button
              variant="contained"
              fullWidth
              size="large"
              onClick={handleInterpret}
              disabled={loading || selectedCurves.length === 0}
              startIcon={loading ? <CircularProgress size={20} /> : <PsychologyIcon />}
            >
              {loading ? 'Generating AI Interpretation...' : 'Generate AI Interpretation'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {interpretation && (
        <Paper elevation={3} sx={{ p: 3, mb: 3, backgroundColor: '#f5f5f5' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PsychologyIcon color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6">AI Interpretation Result</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          <Box sx={{ mb: 2 }}>
            <Chip label={`Depth: ${interpretation.start_depth} - ${interpretation.end_depth} ${file.depth_unit}`} sx={{ mr: 1 }} />
            <Chip label={`Curves: ${interpretation.curves_analyzed.join(', ')}`} />
          </Box>

          <Box sx={{ backgroundColor: 'white', p: 2, borderRadius: 1 }}>
            {formatInterpretation(interpretation.interpretation)}
          </Box>

          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            Generated: {new Date(interpretation.created_at).toLocaleString()} | 
            Model: {interpretation.model_used}
          </Typography>
        </Paper>
      )}

      {pastInterpretations.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mt: 4 }}>
            <HistoryIcon sx={{ mr: 1 }} />
            Past Interpretations
          </Typography>
          
          {pastInterpretations.map((interp, index) => (
            <Card key={interp.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ mb: 1 }}>
                  <Chip 
                    label={`Depth: ${interp.start_depth} - ${interp.end_depth} ${file.depth_unit}`} 
                    size="small" 
                    sx={{ mr: 1 }} 
                  />
                  <Chip 
                    label={`${interp.curves_analyzed.length} curves`} 
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </Box>
                
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 2 }}>
                  {interp.interpretation.substring(0, 300)}
                  {interp.interpretation.length > 300 && '...'}
                </Typography>
                
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {new Date(interp.created_at).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {!interpretation && !loading && pastInterpretations.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            Select curves and depth range, then click "Generate AI Interpretation" 
            to get AI-powered insights about your well-log data.
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default AIInterpretation;
