document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');

    function setLoading(isLoading) {
        uploadBtn.disabled = isLoading;
        uploadBtn.textContent = isLoading ? 'Thinking...' : 'Evaluate';
        loadingDiv.classList.toggle('active', isLoading);
    }

    uploadBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];

        if (!file) {
            resultDiv.innerText = "Please select a file first!";
            return;
        }

        resultDiv.innerText = '';
        setLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/evaluate', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.error) {
                resultDiv.innerText = "Error: " + data.error;
            } else {
                resultDiv.innerText = data.feedback;
            }
        } catch (err) {
            resultDiv.innerText = "Request failed: " + err.message;
        } finally {
            setLoading(false);
        }
    });
});