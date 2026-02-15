from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class WellLogFile(db.Model):
    __tablename__ = 'well_log_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(512), nullable=False)
    s3_url = db.Column(db.String(1024))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)
    
    # LAS file metadata
    well_name = db.Column(db.String(255))
    field_name = db.Column(db.String(255))
    company = db.Column(db.String(255))
    date = db.Column(db.String(100))
    
    # Depth information
    start_depth = db.Column(db.Float)
    stop_depth = db.Column(db.Float)
    step = db.Column(db.Float)
    depth_unit = db.Column(db.String(50), default='M')
    
    # Available curves (stored as JSON)
    available_curves = db.Column(db.Text)  # JSON list of curve names
    
    # Relationships
    curves = db.relationship('CurveData', back_populates='file', cascade='all, delete-orphan')
    interpretations = db.relationship('AIInterpretation', back_populates='file', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            's3_url': self.s3_url,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'file_size': self.file_size,
            'well_name': self.well_name,
            'field_name': self.field_name,
            'company': self.company,
            'date': self.date,
            'start_depth': self.start_depth,
            'stop_depth': self.stop_depth,
            'step': self.step,
            'depth_unit': self.depth_unit,
            'available_curves': json.loads(self.available_curves) if self.available_curves else []
        }


class CurveData(db.Model):
    __tablename__ = 'curve_data'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('well_log_files.id'), nullable=False)
    curve_name = db.Column(db.String(100), nullable=False)
    curve_unit = db.Column(db.String(50))
    curve_description = db.Column(db.String(255))
    
    # Depth and value stored as JSON arrays for efficient retrieval
    depths = db.Column(db.Text, nullable=False)  # JSON array
    values = db.Column(db.Text, nullable=False)  # JSON array
    
    # Statistics
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    mean_value = db.Column(db.Float)
    
    # Relationships
    file = db.relationship('WellLogFile', back_populates='curves')
    
    # Indexes for faster queries
    __table_args__ = (
        db.Index('idx_file_curve', 'file_id', 'curve_name'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_id': self.file_id,
            'curve_name': self.curve_name,
            'curve_unit': self.curve_unit,
            'curve_description': self.curve_description,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'mean_value': self.mean_value
        }
    
    def get_data(self, start_depth=None, end_depth=None):
        """Get curve data, optionally filtered by depth range"""
        depths = json.loads(self.depths)
        values = json.loads(self.values)
        
        if start_depth is None and end_depth is None:
            return depths, values
        
        # Filter by depth range
        filtered_depths = []
        filtered_values = []
        
        for d, v in zip(depths, values):
            if (start_depth is None or d >= start_depth) and \
               (end_depth is None or d <= end_depth):
                filtered_depths.append(d)
                filtered_values.append(v)
        
        return filtered_depths, filtered_values


class AIInterpretation(db.Model):
    __tablename__ = 'ai_interpretations'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('well_log_files.id'), nullable=False)
    
    # Query parameters
    curves_analyzed = db.Column(db.Text)  # JSON array of curve names
    start_depth = db.Column(db.Float)
    end_depth = db.Column(db.Float)
    
    # AI Response
    interpretation = db.Column(db.Text, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_used = db.Column(db.String(100), default='gpt-3.5-turbo')
    
    # Relationships
    file = db.relationship('WellLogFile', back_populates='interpretations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_id': self.file_id,
            'curves_analyzed': json.loads(self.curves_analyzed) if self.curves_analyzed else [],
            'start_depth': self.start_depth,
            'end_depth': self.end_depth,
            'interpretation': self.interpretation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'model_used': self.model_used
        }
