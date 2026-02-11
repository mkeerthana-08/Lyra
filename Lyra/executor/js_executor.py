import shutil
import subprocess
import tempfile


def run_js(code):
    try:
        node_path = shutil.which("node")
        if not node_path:
            return {"output": "", "error": "node not found in PATH."}

        with tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w", encoding="utf-8") as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        run_process = subprocess.run(
            [node_path, temp_file_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        if run_process.returncode != 0:
            return {"output": "", "error": run_process.stderr.strip()}

        return {"output": run_process.stdout.strip(), "error": ""}

    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Execution timed out."}

    except Exception as exc:
        return {"output": "", "error": str(exc)}
