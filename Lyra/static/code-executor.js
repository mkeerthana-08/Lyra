async function runCode() {
    const code = document.getElementById("codeInput").value;
    const language = document.querySelector("select[name='language']").value;
    const outputElement = document.getElementById("codeOutput");

    if (!code.trim()) {
        outputElement.innerText = "Error: No code to run";
        return;
    }

    outputElement.innerText = "▄ Running...";

    try {
        const response = await fetch("/execute", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                code: code,
                language: language
            })
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        if (data.error) {
            outputElement.parentElement.className = "output-error";
            outputElement.innerText = data.error;
        } else if (data.output) {
            outputElement.parentElement.className = "output-success";
            outputElement.innerText = data.output;
        } else {
            outputElement.parentElement.className = "output-placeholder";
            outputElement.innerText = "(No output)";
        }
    } catch (error) {
        outputElement.parentElement.className = "output-error";
        outputElement.innerText = "Error: " + error.message;
    }
}
