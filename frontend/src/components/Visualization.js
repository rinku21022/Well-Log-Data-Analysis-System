import React, { useState, useEffect, useCallback } from 'react';
import Plot from 'react-plotly.js';
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
} from '@mui/material';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import { getCurves, getVisualizationData } from '../services/api';

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

function Visualization({ file }) {
  const [curves, setCurves] = useState([]);
  const [selectedCurves, setSelectedCurves] = useState([]);
  const [startDepth, setStartDepth] = useState(file.start_depth);
  const [endDepth, setEndDepth] = useState(file.stop_depth);
  const [plotData, setPlotData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadCurves = useCallback(async () => {
    try {
      const data = await getCurves(file.id);
      setCurves(data.curves);
      
      // Auto-select first 3 curves
      if (data.curves.length > 0) {
        const defaultSelection = data.curves.slice(0, Math.min(3, data.curves.length));
        setSelectedCurves(defaultSelection.map(c => c.curve_name));
      }
    } catch (err) {
      setError('Error loading curves: ' + (err.response?.data?.error || err.message));
    }
  }, [file.id]);

  useEffect(() => {
    loadCurves();
  }, [loadCurves]);

  const handleCurveChange = (event) => {
    const value = event.target.value;
    setSelectedCurves(typeof value === 'string' ? value.split(',') : value);
  };

  const handleVisualize = async () => {
    if (selectedCurves.length === 0) {
      setError('Please select at least one curve');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getVisualizationData(
        file.id,
        selectedCurves,
        startDepth,
        endDepth
      );

      // Prepare Plotly data
      const traces = data.curves.map((curve, index) => {
        // Create subplot for each curve
        return {
          x: curve.values,
          y: curve.depths,
          type: 'scatter',
          mode: 'lines',
          name: `${curve.name} (${curve.unit})`,
          xaxis: `x${index + 1}`,
          yaxis: 'y',
          line: {
            width: 2,
          },
        };
      });

      setPlotData(traces);
    } catch (err) {
      setError('Error generating visualization: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Create layout for multiple subplots
  const createLayout = () => {
    const numCurves = plotData.length;
    const layout = {
      title: `Well Log Visualization - ${file.filename}`,
      height: 700,
      showlegend: true,
      yaxis: {
        title: `Depth (${file.depth_unit})`,
        autorange: 'reversed',
      },
      grid: {
        rows: 1,
        columns: numCurves,
        pattern: 'independent',
      },
    };

    // Add x-axis for each curve
    plotData.forEach((trace, index) => {
      const axisNum = index + 1;
      layout[`xaxis${axisNum === 1 ? '' : axisNum}`] = {
        title: trace.name,
        side: 'top',
      };
    });

    return layout;
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        <ShowChartIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
        Curve Visualization
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
              onClick={handleVisualize}
              disabled={loading || selectedCurves.length === 0}
            >
              {loading ? <CircularProgress size={24} /> : 'Generate Visualization'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {plotData.length > 0 && (
        <Paper elevation={2} sx={{ p: 2 }}>
          <Plot
            data={plotData}
            layout={createLayout()}
            config={{
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            }}
            style={{ width: '100%', height: '700px' }}
          />
        </Paper>
      )}

      {plotData.length === 0 && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            Select curves and click "Generate Visualization" to display the well-log data.
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default Visualization;
