# python/main.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import threading
import webbrowser
from pyreverse_handler import PyReverseHandler
from diagram_generator import DiagramGenerator

app = Flask(__name__)
CORS(app)

# Global instances
pyreverse_handler = PyReverseHandler()
diagram_generator = DiagramGenerator()


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "pyreverse-gui-backend"})


@app.route("/api/check-dependencies", methods=["GET"])
def check_dependencies():
    """Check if required dependencies are installed"""
    return jsonify(pyreverse_handler.check_dependencies())


@app.route("/api/analyze-project", methods=["POST"])
def analyze_project():
    """Analyze a Python project and return available modules"""
    data = request.json
    project_path = data.get("project_path")

    if not project_path or not os.path.exists(project_path):
        return jsonify({"error": "Invalid project path"}), 400

    try:
        modules = pyreverse_handler.analyze_project(project_path)
        return jsonify({"modules": modules})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-diagram", methods=["POST"])
def generate_diagram():
    """Generate UML diagram using pyreverse"""
    data = request.json

    required_fields = ["project_path", "output_format", "diagram_type"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        result = diagram_generator.generate_diagram(
            project_path=data["project_path"],
            output_format=data["output_format"],
            diagram_type=data["diagram_type"],
            output_name=data.get("output_name", "diagram"),
            options=data.get("options", {}),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get-diagram/<filename>", methods=["GET"])
def get_diagram(filename):
    """Serve generated diagram files"""
    try:
        file_path = os.path.join("dist", filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/list-formats", methods=["GET"])
def list_formats():
    """List available output formats"""
    formats = pyreverse_handler.get_supported_formats()
    return jsonify({"formats": formats})


@app.route("/api/get-options", methods=["GET"])
def get_options():
    """Get available pyreverse options"""
    options = pyreverse_handler.get_available_options()
    return jsonify({"options": options})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
