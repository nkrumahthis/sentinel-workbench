from flask import Flask, jsonify, request
from flask_cors import CORS
from alerts import AlertStore

from enrichment_service import MockAWSEnrichmentService

# Flask API
app = Flask(__name__)
CORS(app)

enrichment_service = MockAWSEnrichmentService()
alert_store = AlertStore()

@app.route("/", methods=["GET"])
def index():
    """Welcome message."""
    return jsonify({"message": "Welcome to the Sentinel Workbench API"})


@app.route("/api/enrich", methods=["POST"])
def enrich_alert():
    try:
        alert_data = request.json
        user_name = alert_data.get("userName")

        if not user_name:
            return jsonify({"error": "userName is required"}), 400

        enrichments = enrichment_service.enrich(user_name, alert_data)

        return jsonify(enrichments)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users", methods=["GET"])
def get_users():
    """Get list of unique users in the mock data."""
    try:
        users = enrichment_service.get_users()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """Get list of all alerts."""
    try:
        # Convert alerts dict to list and sort by timestamp
        alerts_list = list(alert_store.alerts.values())
        alerts_list.sort(key=lambda x: x["timestamp"], reverse=True)
        return jsonify(alerts_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/alerts/<alert_id>", methods=["GET"])
def get_alert(alert_id):
    """Get specific alert details."""
    try:
        alert = alert_store.alerts.get(alert_id)
        if not alert:
            return jsonify({"error": "Alert not found"}), 404
        return jsonify(alert)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
