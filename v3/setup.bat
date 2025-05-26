@echo off
echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt

echo Creating models directory...
if not exist models mkdir models

echo Downloading Mistral model...
if not exist models\mistral-7b-instruct-v0.2.Q4_K_M.gguf (
    curl -L https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf -o models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
) else (
    echo Model already exists, skipping download...
)

echo Setup complete!
echo To activate the virtual environment, run: .venv\Scripts\activate.bat 