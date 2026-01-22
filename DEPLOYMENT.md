# Deployment Guide

This guide provides multiple deployment options for the Hotel Room Reservation System.

## 🚀 Quick Deployment Options

### Option 1: Docker Compose (Recommended - Easiest)

**Best for**: Local development, single-server deployment, quick setup

**Requirements**: Docker & Docker Compose installed

**Steps**:
1. Ensure Docker and Docker Compose are installed
2. Create `.env` files (see below)
3. Run: `docker-compose up -d`
4. Access frontend at `http://localhost:3000`
5. Access backend API at `http://localhost:8001`

**Advantages**:
- ✅ Single command deployment
- ✅ Handles MongoDB automatically
- ✅ Isolated environments
- ✅ Easy to stop/start

---

### Option 2: Manual Deployment

**Best for**: Production servers, custom configurations

**Requirements**: 
- Python 3.9+, Node.js 16+, MongoDB instance

**Steps**:

#### Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create .env file (see below)
uvicorn server:app --host 0.0.0.0 --port 8001
```

#### Frontend Setup:
```bash
cd frontend
yarn install
# Create .env file (see below)
yarn build
# Serve with nginx/apache or use serve:
npx serve -s build -l 3000
```

---

### Option 3: Cloud Platform Deployment

#### A. Railway / Render / Fly.io
- Connect GitHub repo
- Set environment variables
- Auto-deploys on push

#### B. AWS / GCP / Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Or use serverless (Lambda + API Gateway for backend)
- Frontend on S3 + CloudFront / Firebase Hosting / Azure Static Web Apps

#### C. Heroku
- Backend: Add `Procfile` with `web: uvicorn server:app --host 0.0.0.0 --port $PORT`
- Frontend: Use buildpack or deploy separately
- Add MongoDB Atlas addon

---

## 📋 Environment Variables

### Backend `.env` (in `backend/` directory)
```env
MONGO_URL=mongodb://localhost:27017
# OR for MongoDB Atlas:
# MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

DB_NAME=hotel_reservation
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Frontend `.env` (in `frontend/` directory)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
# OR for production:
# REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

---

## 🐳 Docker Deployment Details

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2+

### Quick Start
```bash
# Clone/navigate to project
cd app

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Services
- **Backend**: FastAPI on port 8001
- **Frontend**: React build served on port 3000
- **MongoDB**: Database on port 27017 (internal)

---

## ☁️ Production Deployment Checklist

### Security
- [ ] Use MongoDB Atlas or secured MongoDB instance
- [ ] Set strong MongoDB credentials
- [ ] Configure CORS_ORIGINS to specific domains (not `*`)
- [ ] Use HTTPS for frontend and backend
- [ ] Set up firewall rules
- [ ] Use environment variables (never commit `.env`)

### Performance
- [ ] Enable MongoDB indexes if needed
- [ ] Configure reverse proxy (nginx) for frontend
- [ ] Set up CDN for static assets
- [ ] Configure gzip compression
- [ ] Use production build of React (`yarn build`)

### Monitoring
- [ ] Set up logging (CloudWatch, Datadog, etc.)
- [ ] Configure health checks
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Monitor MongoDB connection pool

### Scaling
- [ ] Use MongoDB Atlas for managed database
- [ ] Consider load balancer for multiple backend instances
- [ ] Use Redis for session management (if adding auth)
- [ ] Configure auto-scaling based on traffic

---

## 🔧 Common Issues & Solutions

### Backend won't start
- Check MongoDB connection string
- Verify Python version (3.9+)
- Check if port 8001 is available
- Review logs: `docker-compose logs backend`

### Frontend can't connect to backend
- Verify `REACT_APP_BACKEND_URL` in frontend `.env`
- Check CORS settings in backend
- Ensure backend is running
- Check browser console for errors

### MongoDB connection errors
- Verify `MONGO_URL` is correct
- Check MongoDB is running (if local)
- For Atlas: Whitelist IP addresses
- Check network connectivity

### Build errors
- Clear node_modules and reinstall: `rm -rf node_modules && yarn install`
- Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`
- Check Node.js version (16+)
- Check Python version (3.9+)

---

## 📊 Recommended Production Architecture

```
Internet
    ↓
[CloudFlare / CDN]
    ↓
[Nginx Reverse Proxy]
    ├─→ [Frontend (Static Files)]
    └─→ [Backend (FastAPI)]
            ↓
    [MongoDB Atlas / Managed DB]
```

---

## 🚢 Deployment Scripts

See `deploy.sh` (Linux/Mac) or `deploy.ps1` (Windows) for automated deployment.

---

## 📞 Support

For deployment issues, check:
1. Logs: `docker-compose logs` or application logs
2. Environment variables are set correctly
3. Ports are not blocked by firewall
4. MongoDB is accessible
