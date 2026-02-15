from flask import Blueprint, request, jsonify
from models import db, WellLogFile, CurveData, AIInterpretation
from utils import AIService
import json

bp = Blueprint('ai', __name__, url_prefix='/api')


@bp.route('/interpret', methods=['POST'])
def interpret():
    """
    Generate AI interpretation of well-log data
    
    Request body:
        {
            "file_id": int,
            "curves": [str],  # List of curve names
            "start_depth": float,
            "end_depth": float
        }
    
    Returns:
        JSON with AI interpretation
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        file_id = data.get('file_id')
        curve_names = data.get('curves', [])
        start_depth = data.get('start_depth')
        end_depth = data.get('end_depth')
        
        if not all([file_id, curve_names, start_depth is not None, end_depth is not None]):
            return jsonify({'error': 'file_id, curves, start_depth, and end_depth are required'}), 400
        
        # Get file
        file = WellLogFile.query.get(file_id)
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        # Prepare curves data for AI
        curves_data = {}
        
        for curve_name in curve_names:
            curve = CurveData.query.filter_by(
                file_id=file_id,
                curve_name=curve_name
            ).first()
            
            if curve:
                depths, values = curve.get_data(start_depth, end_depth)
                
                # Get some sample values
                sample_count = min(5, len(values))
                sample_indices = [int(i * len(values) / sample_count) for i in range(sample_count)]
                sample_values = [f"{depths[i]:.2f}: {values[i]:.2f}" for i in sample_indices if i < len(values)]
                
                curves_data[curve_name] = {
                    'unit': curve.curve_unit,
                    'min_value': min(values) if values else None,
                    'max_value': max(values) if values else None,
                    'mean_value': sum(values) / len(values) if values else None,
                    'sample_values': sample_values
                }
        
        if not curves_data:
            return jsonify({'error': 'No valid curve data found'}), 404
        
        # Prepare well metadata
        well_metadata = {
            'well_name': file.well_name,
            'field_name': file.field_name,
            'company': file.company,
            'depth_unit': file.depth_unit
        }
        
        # Generate interpretation
        try:
            ai_service = AIService()
            interpretation_text = ai_service.interpret_curves(
                curves_data,
                start_depth,
                end_depth,
                well_metadata
            )
        except Exception as e:
            return jsonify({'error': f'AI service error: {str(e)}'}), 500
        
        # Save interpretation to database
        interpretation = AIInterpretation(
            file_id=file_id,
            curves_analyzed=json.dumps(curve_names),
            start_depth=start_depth,
            end_depth=end_depth,
            interpretation=interpretation_text,
            model_used='gemini-2.5-flash'
        )
        
        db.session.add(interpretation)
        db.session.commit()
        
        return jsonify({
            'interpretation': interpretation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error generating interpretation: {str(e)}'}), 500


@bp.route('/interpretations/<int:file_id>', methods=['GET'])
def get_interpretations(file_id):
    """
    Get all interpretations for a file
    
    Args:
        file_id: ID of the file
        
    Returns:
        JSON array of interpretations
    """
    try:
        file = WellLogFile.query.get(file_id)
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        interpretations = AIInterpretation.query.filter_by(
            file_id=file_id
        ).order_by(AIInterpretation.created_at.desc()).all()
        
        return jsonify({
            'interpretations': [i.to_dict() for i in interpretations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving interpretations: {str(e)}'}), 500


@bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat interface for asking questions about well data
    
    Request body:
        {
            "file_id": int,
            "message": str,
            "conversation_history": [{"role": str, "content": str}] (optional)
        }
    
    Returns:
        JSON with AI response
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        file_id = data.get('file_id')
        message = data.get('message')
        conversation_history = data.get('conversation_history', [])
        
        if not file_id or not message:
            return jsonify({'error': 'file_id and message are required'}), 400
        
        # Get file data
        file = WellLogFile.query.get(file_id)
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        # Prepare well data context
        well_data = file.to_dict()
        
        # Generate response
        try:
            ai_service = AIService()
            response_text = ai_service.chat_about_data(
                message,
                well_data,
                conversation_history
            )
        except Exception as e:
            return jsonify({'error': f'AI service error: {str(e)}'}), 500
        
        from datetime import datetime
        return jsonify({
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error in chat: {str(e)}'}), 500
