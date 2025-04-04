# 🌱 Carbon Footprint API

A lightweight API for calculating carbon footprint, secured with JWT authentication. Built and deployed using Docker.

## 🐳 Getting Started

To run the application, use the following command:

```bash
docker-compose up

The API will be available at:
http://localhost:8000
```

To run tests, use the following command:
```bash

pytest
``` 

📘 API Documentation
You can access the interactive Swagger UI at:

http://localhost:8000/docs

🔐 Authentication
Use the credentials defined in your .env file to authenticate:

```bash
USERNAME=testuser
PASSWORD=testpassword
```

After logging in via the Swagger UI, a JWT token will be generated and used automatically for authenticated requests.

📡 Endpoints
- POST /token
Authenticates the user and returns a JWT token.


- POST /carbon-footprint
Calculates the carbon footprint based on input data.

Requires a valid JWT token in the Authorization header.

⚙️ Environment Variables
.env is already in a version-control for a demo-purpose


🛠 Built With
Docker

Docker Compose

FastAPI (or your framework of choice)







