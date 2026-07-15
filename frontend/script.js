const fileInput = document.getElementById("fileInput");
const evaluateButton = document.getElementById("evaluateButton");
const statusEl = document.getElementById("status");
const metaEl = document.getElementById("meta");
const resultEl = document.getElementById("result");

const fallbackEndpoint = "https://project-invent-ai-reviewer.vercel.app/api/evaluate";
const endpoint = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ? "http://127.0.0.1:8000/api/evaluate.json"
  : (window.API_BASE_URL || fallbackEndpoint);

async function readFile(file) {
  if (!file) {
    throw new Error("Please choose a file first.");
  }

  const text = await file.text();
  return {
    fileName: file.name,
    size: file.size,
    content: text,
  };
}

evaluateButton.addEventListener("click", async () => {
  try {
    statusEl.textContent = "Reading file...";
    const payload = await readFile(fileInput.files[0]);
    metaEl.textContent = `File: ${payload.fileName} • ${payload.size} bytes`;
    statusEl.textContent = "Evaluating...";

    const response = await fetch(endpoint, {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }

    const data = await response.json();
    resultEl.textContent = JSON.stringify(data, null, 2);
    statusEl.textContent = data.mock ? "Received a mock review response." : "Evaluation complete.";
  } catch (error) {
    resultEl.textContent = `Error: ${error.message}`;
    statusEl.textContent = "Evaluation failed.";
  }
});
