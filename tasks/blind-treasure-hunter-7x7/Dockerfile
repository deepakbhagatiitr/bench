FROM apex_arena:base

# Use root to copy/setup, then drop back to model later (matches Apex base image pattern)
USER root

# Workdir for the agent
WORKDIR /workdir

# Copy runtime env and reference solver
COPY env.py /workdir/env.py
COPY explorer.py /workdir/explorer.py
COPY solution.sh /workdir/solution.sh
RUN chmod +x /workdir/solution.sh

# Minimal system deps (Python is available in base; if not, uncomment below)
# RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
    
# Lock down: nothing extra installed; pure-CLI interaction via env.py

# Return to model user for evaluation
USER root


# Optional: make it easy for the agent to see helper doc
RUN echo "Run: python /workdir/env.py init | pos | look | move N|S|E|W | scan | dims" > /workdir/README_AGENT.txt
