import os
import re
import subprocess
import tempfile


def run_java(code):
    try:
        match = re.search(r"public\s+class\s+(\w+)", code)
        if not match:
            return {"output": "", "error": "Java code must contain a public class."}

        class_name = match.group(1)

        with tempfile.TemporaryDirectory() as tmpdir:
            java_file = os.path.join(tmpdir, f"{class_name}.java")

            with open(java_file, "w", encoding="utf-8") as handle:
                handle.write(code)

            compile_process = subprocess.run(
                ["javac", java_file],
                capture_output=True,
                text=True,
                timeout=10
            )

            if compile_process.returncode != 0:
                return {"output": "", "error": compile_process.stderr.strip()}

            run_process = subprocess.run(
                ["java", "-cp", tmpdir, class_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if run_process.returncode != 0:
                return {"output": "", "error": run_process.stderr.strip()}

            return {"output": run_process.stdout.strip(), "error": ""}

    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Execution timed out."}

    except Exception as exc:
        return {"output": "", "error": str(exc)}
