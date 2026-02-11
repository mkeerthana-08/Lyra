import os
import shutil
import subprocess
import tempfile


def run_cpp(code):
    try:
        compiler = shutil.which("g++")
        if not compiler:
            return {"output": "", "error": "g++ not found in PATH."}

        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = os.path.join(tmpdir, "main.cpp")
            output_file = os.path.join(tmpdir, "program.exe" if os.name == "nt" else "program")

            with open(source_file, "w", encoding="utf-8") as handle:
                handle.write(code)

            compile_process = subprocess.run(
                [compiler, source_file, "-std=c++17", "-o", output_file],
                capture_output=True,
                text=True,
                timeout=10
            )

            if compile_process.returncode != 0:
                return {"output": "", "error": compile_process.stderr.strip()}

            run_process = subprocess.run(
                [output_file],
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
