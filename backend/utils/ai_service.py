import google.generativeai as genai
import os
from typing import List, Dict, Any
import json


class AIService:
    """Service for AI-powered interpretation of well-log data using Google Gemini"""
    
    def __init__(self):
        """Initialize Google Gemini client"""
        api_key = os.getenv('GEMINI_API_KEY')
        print(f"DEBUG: GEMINI_API_KEY = {'SET' if api_key else 'NOT SET'}, Length = {len(api_key) if api_key else 0}")
        if not api_key or api_key.strip() == '':
            self.enabled = False
            print("Warning: GEMINI_API_KEY not set. AI features will be disabled.")
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('models/gemini-2.5-flash')
                self.enabled = True
                print("SUCCESS: Gemini AI configured and enabled!")
            except Exception as e:
                self.enabled = False
                print(f"ERROR configuring Gemini: {str(e)}")
    
    def interpret_curves(
        self, 
        curves_data: Dict[str, Dict[str, Any]],
        start_depth: float,
        end_depth: float,
        well_metadata: Dict = None
    ) -> str:
        """
        Generate AI interpretation of well-log curves
        
        Args:
            curves_data: Dictionary mapping curve names to their data and statistics
            start_depth: Start of depth range
            end_depth: End of depth range
            well_metadata: Optional metadata about the well
            
        Returns:
            AI-generated interpretation as string
        """
        if not self.enabled:
            return """AI Interpretation Service is currently unavailable.
            
To enable AI features:
1. Get a FREE API key from https://aistudio.google.com/app/apikey
2. Add it to backend/.env as: GEMINI_API_KEY=your-key-here
3. Restart the backend server

Note: Google Gemini has a generous FREE tier with 60 requests per minute - perfect for this application!"""
        
        # Prepare context for AI
        context = self._prepare_interpretation_context(
            curves_data, start_depth, end_depth, well_metadata
        )
        
        # Create prompt
        prompt = f"""You are a geoscience expert analyzing well-log data. Provide a detailed interpretation of the following well-log measurements.

{context}

Please provide:
1. General overview of the depth interval
2. Analysis of each curve and what it indicates
3. Potential lithology (rock type) interpretation
4. Any notable trends or anomalies
5. Hydrocarbon potential indicators (if applicable)

Be specific and reference actual values from the data."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating interpretation: {str(e)}"
    
    def _prepare_interpretation_context(
        self,
        curves_data: Dict[str, Dict[str, Any]],
        start_depth: float,
        end_depth: float,
        well_metadata: Dict = None
    ) -> str:
        """Prepare context string for AI interpretation"""
        context_parts = []
        
        # Add well metadata if available
        if well_metadata:
            context_parts.append("Well Information:")
            if well_metadata.get('well_name'):
                context_parts.append(f"- Well Name: {well_metadata['well_name']}")
            if well_metadata.get('field_name'):
                context_parts.append(f"- Field: {well_metadata['field_name']}")
            if well_metadata.get('company'):
                context_parts.append(f"- Company: {well_metadata['company']}")
            context_parts.append("")
        
        # Add depth range
        context_parts.append(f"Depth Range: {start_depth} to {end_depth} {well_metadata.get('depth_unit', 'M')}")
        context_parts.append("")
        
        # Add curve statistics
        context_parts.append("Curve Data Summary:")
        for curve_name, data in curves_data.items():
            context_parts.append(f"\n{curve_name} ({data.get('unit', '')}:")
            context_parts.append(f"  - Minimum: {data.get('min_value', 'N/A')}")
            context_parts.append(f"  - Maximum: {data.get('max_value', 'N/A')}")
            context_parts.append(f"  - Average: {data.get('mean_value', 'N/A')}")
            
            # Add sample values if available
            if 'sample_values' in data:
                context_parts.append(f"  - Sample values: {data['sample_values']}")
        
        return "\n".join(context_parts)
    
    def chat_about_data(
        self,
        user_message: str,
        well_data: Dict[str, Any],
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Chat interface for asking questions about well data
        
        Args:
            user_message: User's question
            well_data: Complete well data context
            conversation_history: Previous messages in conversation
            
        Returns:
            AI response as string
        """
        if not self.enabled:
            return """Chatbot service is currently unavailable.

To enable the chatbot:
1. Get a FREE API key from https://aistudio.google.com/app/apikey
2. Add it to backend/.env as: GEMINI_API_KEY=your-key-here
3. Restart the backend server

Google Gemini offers a generous FREE tier - 60 requests per minute!
You can still use the visualization and file management features without AI."""
        
        # Prepare data context
        data_context = self._prepare_chat_context(well_data)
        
        # Build complete prompt with context
        system_context = f"""You are a helpful assistant specialized in well-log data analysis. 

You have access to the following well data:
{data_context}

Answer questions about this data accurately and helpfully. If asked about specific values, reference the data provided. If the information isn't available in the data, say so."""
        
        # Combine system context with conversation history
        full_prompt = system_context + "\n\n"
        
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'user':
                    full_prompt += f"User: {content}\n"
                elif role == 'assistant':
                    full_prompt += f"Assistant: {content}\n"
        
        full_prompt += f"\nUser: {user_message}\nAssistant:"
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            return f"Error in chat: {str(e)}"
    
    def _prepare_chat_context(self, well_data: Dict[str, Any]) -> str:
        """Prepare well data context for chat"""
        context_parts = []
        
        # Well information
        context_parts.append("Well Information:")
        for key in ['well_name', 'field_name', 'company', 'date']:
            if key in well_data and well_data[key]:
                context_parts.append(f"- {key.replace('_', ' ').title()}: {well_data[key]}")
        
        # Depth information
        context_parts.append(f"\nDepth Range: {well_data.get('start_depth')} to {well_data.get('stop_depth')} {well_data.get('depth_unit', 'M')}")
        
        # Available curves
        if 'available_curves' in well_data:
            context_parts.append(f"\nAvailable Curves: {', '.join(well_data['available_curves'])}")
        
        return "\n".join(context_parts)
