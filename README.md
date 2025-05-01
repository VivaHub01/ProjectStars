# Start
# Create network
docker network create app-network
# Run backend/frontend
docker-compose up --build
# Backend
http://127.0.0.1:8000/docs
# Frontend
http://localhost:3000

