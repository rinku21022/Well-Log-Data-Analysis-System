from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import json

from models import db, WellLogFile, CurveData
from utils import LASParser, LocalStorageService

bp = Blueprint('upload', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'las', 'LAS'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """
    Upload and process a LAS file
    
    Returns:
        JSON response with file information
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return '', 200
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .las files are allowed'}), 400
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.las') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        # Parse LAS file
        try:
            parser = LASParser(temp_path)
            metadata = parser.get_metadata()
            available_curves = parser.get_available_curves()
            curves_data = parser.get_all_curves_data()
        except Exception as e:
            os.unlink(temp_path)
            return jsonify({'error': f'Error parsing LAS file: {str(e)}'}), 400
        
        # Upload to local storage (free, no AWS needed)
        try:
            storage_service = LocalStorageService()
            storage_result = storage_service.upload_file(temp_path, filename)
            
            if not storage_result['success']:
                os.unlink(temp_path)
                return jsonify({'error': f'Error uploading to storage: {storage_result.get("error")}'}), 500
        except Exception as e:
            os.unlink(temp_path)
            return jsonify({'error': f'Storage service error: {str(e)}'}), 500
        
        # Get file size
        file_size = os.path.getsize(temp_path)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Create database entry for file
        well_file = WellLogFile(
            filename=filename,
            s3_key=storage_result['storage_key'],
            s3_url=storage_result['file_url'],
            file_size=file_size,
            well_name=metadata.get('well_name'),
            field_name=metadata.get('field_name'),
            company=metadata.get('company'),
            date=metadata.get('date'),
            start_depth=metadata.get('start_depth'),
            stop_depth=metadata.get('stop_depth'),
            step=metadata.get('step'),
            depth_unit=metadata.get('depth_unit'),
            available_curves=json.dumps([c['name'] for c in available_curves])
        )
        
        db.session.add(well_file)
        db.session.flush()  # Get the ID
        
        # Store curve data
        for curve_info in available_curves:
            curve_name = curve_info['name']
            
            if curve_name in curves_data:
                depths, values = curves_data[curve_name]
                
                # Calculate statistics
                stats = parser.get_statistics(curve_name)
                
                curve_data = CurveData(
                    file_id=well_file.id,
                    curve_name=curve_name,
                    curve_unit=curve_info['unit'],
                    curve_description=curve_info['description'],
                    depths=json.dumps(depths),
                    values=json.dumps(values),
                    min_value=stats['min'],
                    max_value=stats['max'],
                    mean_value=stats['mean']
                )
                
                db.session.add(curve_data)
        
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': well_file.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
