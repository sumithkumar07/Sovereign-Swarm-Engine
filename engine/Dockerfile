# Use a clean Python base
FROM python:3.11-slim

# Install C++ compiler
RUN apt-get update && apt-get install -y g++ && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all engine files
COPY . .

# Compile the Sovereign Native Engine into a Shared Object (.so)
# This uses zero-dependency C++ for maximum throughput on the HF CPU
RUN g++ -O3 -fPIC -shared sovereign_v9_swarm.cpp -o libsovereign.so

# Install Python bridge requirements
RUN pip install --no-cache-dir -r ../requirements.txt

# Start the Cloud Brain on the default Hugging Face port
EXPOSE 7860
CMD ["python", "main.py"]
