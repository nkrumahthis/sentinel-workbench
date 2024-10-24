from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from enrichment_service import MockAWSEnrichmentService

# Flask API
app = Flask(__name__)
CORS(app)

enrichment_service = MockAWSEnrichmentService()

@app.route('/api/enrich', methods=['POST'])
def enrich_alert():
    try:
        alert_data = request.json
        user_name = alert_data.get('userName')
        
        if not user_name:
            return jsonify({'error': 'userName is required'}), 400
        
        enrichments = enrichment_service.enrich(user_name, alert_data)
        
        return jsonify(enrichments)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get list of unique users in the mock data."""
    try:
        users = set()
        for event in enrichment_service.events:
            user_name = event['userIdentity'].get('userName')
            if user_name:
                users.add(user_name)
        return jsonify(list(users))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


if __name__ == '__main__':
    app.run(debug=True, port=5001)