#Base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies, including Rust
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libssl-dev \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && export PATH="$HOME/.cargo/bin:$PATH"

# Ensure Rust and Cargo are on PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app will run on
EXPOSE 8000

# Define the command to run your application
CMD ["uvicorn", "main:APP", "--host", "0.0.0.0", "--port", "8000"]