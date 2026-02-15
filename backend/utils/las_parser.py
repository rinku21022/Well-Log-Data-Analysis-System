import lasio
import numpy as np
from typing import Dict, List, Tuple
import pandas as pd


class LASParser:
    """Parser for LAS (Log ASCII Standard) files"""
    
    def __init__(self, file_path: str):
        """
        Initialize parser with LAS file path
        
        Args:
            file_path: Path to LAS file
        """
        self.las = lasio.read(file_path)
        self.file_path = file_path
    
    def get_metadata(self) -> Dict:
        """Extract metadata from LAS file"""
        well_info = self.las.well
        
        metadata = {
            'well_name': self._get_header_value(well_info, 'WELL'),
            'field_name': self._get_header_value(well_info, 'FLD'),
            'company': self._get_header_value(well_info, 'COMP'),
            'date': self._get_header_value(well_info, 'DATE'),
            'start_depth': float(self.las.well['STRT'].value) if 'STRT' in self.las.well else None,
            'stop_depth': float(self.las.well['STOP'].value) if 'STOP' in self.las.well else None,
            'step': float(self.las.well['STEP'].value) if 'STEP' in self.las.well else None,
            'depth_unit': self._get_header_value(well_info, 'STRT', get_unit=True) or 'M',
        }
        
        return metadata
    
    def _get_header_value(self, section, key: str, get_unit: bool = False):
        """Helper to safely extract header values"""
        try:
            if key in section:
                if get_unit:
                    return section[key].unit
                return section[key].value
        except:
            pass
        return None
    
    def get_available_curves(self) -> List[Dict]:
        """Get list of available curves with metadata"""
        curves = []
        
        for curve in self.las.curves:
            if curve.mnemonic.upper() != 'DEPT' and curve.mnemonic.upper() != 'DEPTH':
                curves.append({
                    'name': curve.mnemonic,
                    'unit': curve.unit or '',
                    'description': curve.descr or ''
                })
        
        return curves
    
    def get_curve_names(self) -> List[str]:
        """Get list of curve names (excluding depth)"""
        return [c['name'] for c in self.get_available_curves()]
    
    def get_curve_data(self, curve_name: str) -> Tuple[List[float], List[float]]:
        """
        Get depth and values for a specific curve
        
        Args:
            curve_name: Name of the curve to extract
            
        Returns:
            Tuple of (depths, values) as lists
        """
        try:
            # Get depth column
            depth_col = self.las.depth_ft if hasattr(self.las, 'depth_ft') else self.las.index
            
            # Get curve data
            curve_data = self.las[curve_name]
            
            # Convert to lists, handling NaN values
            depths = []
            values = []
            
            for d, v in zip(depth_col, curve_data):
                # Skip NaN or None values
                if not (np.isnan(d) or np.isnan(v) or d is None or v is None):
                    depths.append(float(d))
                    values.append(float(v))
            
            return depths, values
            
        except Exception as e:
            raise ValueError(f"Error extracting curve '{curve_name}': {str(e)}")
    
    def get_all_curves_data(self) -> Dict[str, Tuple[List[float], List[float]]]:
        """
        Get data for all curves
        
        Returns:
            Dictionary mapping curve names to (depths, values) tuples
        """
        curves_data = {}
        
        for curve_name in self.get_curve_names():
            try:
                curves_data[curve_name] = self.get_curve_data(curve_name)
            except Exception as e:
                print(f"Warning: Could not extract curve '{curve_name}': {str(e)}")
                continue
        
        return curves_data
    
    def get_statistics(self, curve_name: str) -> Dict:
        """
        Calculate statistics for a curve
        
        Args:
            curve_name: Name of the curve
            
        Returns:
            Dictionary with min, max, mean, std statistics
        """
        _, values = self.get_curve_data(curve_name)
        
        if not values:
            return {
                'min': None,
                'max': None,
                'mean': None,
                'std': None
            }
        
        values_array = np.array(values)
        
        return {
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'mean': float(np.mean(values_array)),
            'std': float(np.std(values_array))
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert LAS data to pandas DataFrame"""
        return self.las.df()
    
    def get_depth_range(self) -> Tuple[float, float]:
        """Get the actual depth range from data"""
        depth_col = self.las.depth_ft if hasattr(self.las, 'depth_ft') else self.las.index
        return float(np.min(depth_col)), float(np.max(depth_col))
