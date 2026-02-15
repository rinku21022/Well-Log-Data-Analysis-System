from flask import Blueprint, jsonify
from models import db, WellLogFile, CurveData

bp = Blueprint('files', __name__, url_prefix='/api')


@bp.route('/files', methods=['GET'])
def get_files():
    """
    Get list of all uploaded files
    
    Returns:
        JSON array of file objects
    """
    try:
        files = WellLogFile.query.order_by(WellLogFile.upload_date.desc()).all()
        return jsonify({
            'files': [f.to_dict() for f in files]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error retrieving files: {str(e)}'}), 500


@bp.route('/file/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """
    Get details of a specific file
    
    Args:
        file_id: ID of the file
        
    Returns:
        JSON object with file details
    """
    try:
        file = WellLogFile.query.get(file_id)
        
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({
            'file': file.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving file: {str(e)}'}), 500


@bp.route('/curves/<int:file_id>', methods=['GET'])
def get_curves(file_id):
    """
    Get available curves for a file
    
    Args:
        file_id: ID of the file
        
    Returns:
        JSON array of curve objects
    """
    try:
        file = WellLogFile.query.get(file_id)
        
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        curves = CurveData.query.filter_by(file_id=file_id).all()
        
        return jsonify({
            'curves': [c.to_dict() for c in curves]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving curves: {str(e)}'}), 500


@bp.route('/file/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """
    Delete a file and all associated data
    
    Args:
        file_id: ID of the file
        
    Returns:
        JSON success message
    """
    try:
        file = WellLogFile.query.get(file_id)
        
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        # Delete from local storage
        try:
            from utils import LocalStorageService
            storage_service = LocalStorageService()
            storage_service.delete_file(file.s3_key)
        except Exception as e:
            print(f"Warning: Error deleting from storage: {e}")
        
        # Delete from database (cascades to curves and interpretations)
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({
            'message': 'File deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting file: {str(e)}'}), 500
