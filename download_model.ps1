# Placeholder PowerShell script: model download typically requires manual consent on Hugging Face.
# This script prints instructions and shows an example curl command that might work if you have an HF token.

Write-Host "Model download helper (template). Many models require you to accept license on Hugging Face before downloading."
Write-Host "If you have an HF token and a direct URL, you can use the following pattern (example commented):"

Write-Host "# Example (uncomment and replace placeholders):"
Write-Host "# $hf_token = '<YOUR_HF_TOKEN>'"
Write-Host "# $url = 'https://huggingface.co/xxxx/resolve/main/model.gguf'"
Write-Host "# curl -L -H `"Authorization: Bearer $hf_token`" $url -o models/model.gguf"

Write-Host "Otherwise, go to the model page, accept the license, and download the file manually into models/model.gguf"
