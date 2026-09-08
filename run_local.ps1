# PowerShell helper to create venv, install requirements, and run the app

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Start the service
python main.py

# Note: Ensure you have placed a gguf/ggml model at models/model.gguf or set the MODEL_PATH environment variable.
