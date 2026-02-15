from flask import Blueprint, request, jsonify
from models import db, WellLogFile, CurveData
import json

bp = Blueprint('visualization', __name__, url_prefix='/api')


@bp.route('/visualize', methods=['POST'])
def visualize():
    """
    Get curve data for visualization
    
    Request body:
        {
            "file_id": int,
            "curves": [str],  # List of curve names
            "start_depth": float (optional),
            "end_depth": float (optional)
        }
    
    Returns:
        JSON with curve data for plotting
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        file_id = data.get('file_id')
        curve_names = data.get('curves', [])
        start_depth = data.get('start_depth')
        end_depth = data.get('end_depth')
        
        if not file_id:
            return jsonify({'error': 'file_id is required'}), 400
        
        if not curve_names:
            return jsonify({'error': 'At least one curve must be specified'}), 400
        
        # Check if file exists
        file = WellLogFile.query.get(file_id)
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        # Get curve data
        result = {
            'file_info': {
                'filename': file.filename,
                'well_name': file.well_name,
                'start_depth': file.start_depth,
                'stop_depth': file.stop_depth,
                'depth_unit': file.depth_unit
            },
            'curves': []
        }
        
        for curve_name in curve_names:
            curve = CurveData.query.filter_by(
                file_id=file_id,
                curve_name=curve_name
            ).first()
            
            if not curve:
                continue
            
            # Get data with optional depth filtering
            depths, values = curve.get_data(start_depth, end_depth)
            
            result['curves'].append({
                'name': curve.curve_name,
                'unit': curve.curve_unit,
                'description': curve.curve_description,
                'depths': depths,
                'values': values,
                'statistics': {
                    'min': curve.min_value,
                    'max': curve.max_value,
                    'mean': curve.mean_value
                }
            })
        
        if not result['curves']:
            return jsonify({'error': 'No valid curves found'}), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error generating visualization data: {str(e)}'}), 500


@bp.route('/depth-range/<int:file_id>', methods=['GET'])
def get_depth_range(file_id):
    """
    Get the depth range for a file
    
    Args:
        file_id: ID of the file
        
    Returns:
        JSON with start and stop depth
    """
    try:
        file = WellLogFile.query.get(file_id)
        
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({
            'start_depth': file.start_depth,
            'stop_depth': file.stop_depth,
            'step': file.step,
            'depth_unit': file.depth_unit
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving depth range: {str(e)}'}), 500
