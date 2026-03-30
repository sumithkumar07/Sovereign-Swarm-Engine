# Stage 1: Build the C++ Engine
FROM python:3.11-slim as builder

# Install C++ compiler
RUN apt-get update && apt-get install -y g++ && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY sovereign_v9_swarm.cpp .

# Compile the Sovereign Native Engine into a Shared Object (.so)
# This uses zero-dependency C++ for maximum throughput on the HF CPU
RUN g++ -O3 -fPIC -shared sovereign_v9_swarm.cpp -o libsovereign.so

# Stage 2: Final Image
FROM python:3.11-slim

# Create a non-root user (Hugging Face best practice)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy built engine from builder
COPY --from=builder /app/libsovereign.so .

# Copy source and requirements
COPY --chown=user requirements.txt .
COPY --chown=user main.py .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Start the Cloud Brain on the default Hugging Face port
EXPOSE 7860
CMD ["python", "main.py"]
