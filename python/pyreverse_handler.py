import subprocess
import os
import sys
import shutil
from pathlib import Path
import tempfile


class PyReverseHandler:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        dependencies = {"pylint": False, "graphviz": False, "python": False}

        # Check Python
        dependencies["python"] = sys.version_info >= (3, 8)

        # Check pylint (which includes pyreverse)
        try:
            result = subprocess.run(
                ["python", "-m", "pylint", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            dependencies["pylint"] = result.returncode == 0
        except:
            dependencies["pylint"] = False

        # Check Graphviz
        try:
            result = subprocess.run(
                ["dot", "-V"], capture_output=True, text=True, timeout=10
            )
            dependencies["graphviz"] = result.returncode == 0
        except:
            dependencies["graphviz"] = False

        return {"dependencies": dependencies, "all_ready": all(dependencies.values())}

    def analyze_project(self, project_path):
        """Analyze a Python project and return available modules"""
        modules = []

        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common non-code directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", "venv", "env", ".git"]
            ]

            for file in files:
                if file.endswith(".py") and not file.startswith("."):
                    relative_path = os.path.relpath(
                        os.path.join(root, file), project_path
                    )
                    module_name = relative_path.replace(os.sep, ".").replace(".py", "")
                    modules.append(
                        {
                            "name": module_name,
                            "path": relative_path,
                            "is_package": file == "__init__.py",
                        }
                    )

        return modules

    def get_supported_formats(self):
        """Get list of supported output formats"""
        # Standard formats supported by pyreverse
        formats = [
            {"name": "DOT", "extension": ".dot", "description": "Graphviz DOT format"},
            {"name": "PNG", "extension": ".png", "description": "PNG image"},
            {"name": "SVG", "extension": ".svg", "description": "SVG vector image"},
            {
                "name": "PlantUML",
                "extension": ".puml",
                "description": "PlantUML format",
            },
            {"name": "Mermaid", "extension": ".mmd", "description": "MermaidJS format"},
            {"name": "PDF", "extension": ".pdf", "description": "PDF document"},
            {"name": "JPEG", "extension": ".jpg", "description": "JPEG image"},
        ]

        # Check which formats are actually available
        available_formats = []
        for fmt in formats:
            if fmt["extension"] in [".dot", ".puml", ".mmd"]:
                # These are always available
                available_formats.append(fmt)
            else:
                # These require Graphviz
                if self.check_dependencies()["dependencies"]["graphviz"]:
                    available_formats.append(fmt)

        return available_formats

    def get_available_options(self):
        """Get available pyreverse command line options"""
        return {
            "diagram_options": {
                "show_ancestors": {
                    "flag": "-a",
                    "description": "Show ancestors (inheritance levels)",
                    "type": "int",
                    "default": 0,
                },
                "show_associated": {
                    "flag": "-s",
                    "description": "Show associated classes",
                    "type": "int",
                    "default": 0,
                },
                "show_builtin": {
                    "flag": "-b",
                    "description": "Show builtin objects",
                    "type": "boolean",
                    "default": False,
                },
                "module_names": {
                    "flag": "-m",
                    "description": "Show module names",
                    "type": "boolean",
                    "default": False,
                },
                "only_classnames": {
                    "flag": "-k",
                    "description": "Show only class names",
                    "type": "boolean",
                    "default": False,
                },
                "show_dependencies": {
                    "flag": "-d",
                    "description": "Show dependencies",
                    "type": "boolean",
                    "default": True,
                },
            },
            "filter_options": {
                "ignore_patterns": {
                    "flag": "--ignore",
                    "description": "Ignore files/directories matching pattern",
                    "type": "string",
                    "default": "",
                },
                "filter_mode": {
                    "flag": "--filter-mode",
                    "description": "Filter mode for classes",
                    "type": "select",
                    "options": ["PUB_ONLY", "ALL"],
                    "default": "PUB_ONLY",
                },
            },
        }
