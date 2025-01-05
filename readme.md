## Project Setup: Installing Ollama and Llama Model
### Step 1: Install Ollama and Download the Llama Model
Download Ollama
Go to Ollama's download page and install it.
(https://ollama.com/download)

Verify Installation
Open a command prompt and enter:
```
ollama
```
Download the Desired Model
To pull the Llama 3.2 model, run:
```
ollama pull llama3.2
```
Run the Model Locally
Start the model with:
```
ollama run llama3.2
```
Your Llama 3.2 model is now ready for use locally.

### Step 2: Integrating with Streamlit
Set Up a Virtual Environment
Install virtualenv:
```
pip install virtualenv
```
Create a Virtual Environment
Run the following command:
```
python -m venv venv
```
Activate the Virtual Environment
Navigate to the venv folder:
```
cd venv
cd Scripts
activate
```
Install Required Libraries
From within the virtual environment, install dependencies:
```
pip install -r requirements.txt
```
### Step 3: Running the Code
Navigate to the Project Directory
Go to the directory containing chatbot.py.

Run the Streamlit App
Start the app with:
```
streamlit run chatbot.py
```