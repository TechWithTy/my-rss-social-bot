from flask import Flask, request, jsonify
import os
import sys
import json

# Add the project root to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.generate_yaml import save_to_yaml

app = Flask(__name__)

@app.route('/api/config', methods=['POST'])
def save_config():
    """
    API endpoint to receive a configuration dictionary and save it as a YAML file.
    
    Expected JSON format:
    {
        "config_data": {
            "user_profile": {...},
            "social_media_to_post_to": {...},
            "ai": {...},
            "hashtags": {...}
        },
        "filename": "custom_config.yaml"  # Optional, defaults to "config.yaml"
    }
    
    Returns:
        JSON response with status and file path
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'config_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing config_data in request'
            }), 400
        
        config_data = data['config_data']
        filename = data.get('filename', 'config.yaml')
        
        # Save the configuration to YAML
        save_to_yaml(config_data, filename)
                
        filename = "custom_config.yaml"
        file_path = os.path.join('_configs', filename)
        file_path = file_path.replace("\\", "/")
        # Return success response
        return jsonify({
            'status': 'success',
            'message': f'YAML file saved successfully',
            'file_path': file_path
        }), 200
        
    except Exception as e:
        # Return error response
        return jsonify({
            'status': 'error',
            'message': f'Error saving YAML file: {str(e)}'
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config_info():
    """
    API endpoint to get information about available configuration files.
    
    Returns:
        JSON response with list of available configuration files
    """
    try:
        config_dir = "_configs"
        
        # Check if the directory exists
        if not os.path.exists(config_dir):
            return jsonify({
                'status': 'success',
                'message': 'No configuration files found',
                'files': []
            }), 200
        
        # Get list of YAML files in the directory
        yaml_files = [f for f in os.listdir(config_dir) 
                     if os.path.isfile(os.path.join(config_dir, f)) 
                     and (f.endswith('.yaml') or f.endswith('.yml'))]
        
        # Return list of files
        return jsonify({
            'status': 'success',
            'message': f'Found {len(yaml_files)} configuration files',
            'files': yaml_files
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving configuration files: {str(e)}'
        }), 500

# Run the Flask app if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True, port=5000)