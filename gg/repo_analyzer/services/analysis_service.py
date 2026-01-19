import tempfile
import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

class AnalysisService:
    def run_bandit(self, code_content):
        """
        Run bandit security scan on the code content.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code_content)
            temp_file_path = temp_file.name

        try:
            # Run bandit
            # -f json: Output format JSON
            # -ll: Log level (scan level)
            cmd = ["bandit", "-f", "json", "-ll", temp_file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Bandit returns exit code 1 if issues found, so we check stdout
            output = result.stdout
            if output.strip():
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse bandit output", "raw": output}
            return {"results": []}
            
        except Exception as e:
            logger.error(f"Bandit scan failed: {e}")
            return {"error": str(e)}
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def analyze_complexity(self, code_content):
        # We could use radon here
        pass
