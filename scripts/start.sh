#!/bin/bash
# Start script for Mac/Linux

echo "Starting Project Management MVP..."
docker-compose up --build -d

echo ""
echo "Application starting..."
echo "Visit http://localhost:8000 when ready"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: ./scripts/stop.sh"

# Made with Bob
