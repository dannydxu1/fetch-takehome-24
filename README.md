# Project Setup

This guide will walk you through setting up my project, including creating a virtual environment, installing dependencies, running the Flask server, and executing the test script.

## Prerequisites

- Python 3.x installed on your system
- `pip` (Python package installer)
- `bash` for running the test script (`./test.sh`)

## Testing Steps
### Setting Up the Virtual Environment
To create a virtual environment and activate it, follow these steps for Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
### Installing Dependencies
Now that the virtual environment is activated, install the dependencies from the provided file.
```bash
pip install -r requirements.txt
```
### Running the Server
With the depedencies installed, activate the Flask server which will run on http://127.0.0.1:8000.
```bash
python3 server.py
```
### Testing the API Routes
To test the validity of the API routes, I have created a bash script. To run, first change the permissions then execute the file.
```bash
chmod +x ./test.sh
./test.sh
```
### Cleanup
Once finish, don't forget to deactivate the virtual environment and shut down the server process.
```bash
deactivate
```
