#!/bin/bash
set -e
echo '🚀 Westval Setup Started'
mkdir -p backend/logs frontend/build
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
cp .env.example .env 2>/dev/null || true
echo '✅ Setup Complete - Ready for testing'
echo '📋 Start with: docker-compose up'
