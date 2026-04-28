# Use Python 3.9
FROM python:3.9

# Set the working directory
WORKDIR /code

# Copy requirements and install
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of your code
COPY . .

# Expose the ports
EXPOSE 8000
EXPOSE 7860

# Command to run the FastAPI backend in the background AND the Streamlit frontend
# Hugging Face Spaces look for an app running on port 7860
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run dashboard.py --server.port 7860 --server.address 0.0.0.0"]