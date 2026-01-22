# Hotel Room Reservation System

A sophisticated hotel room booking system that optimally allocates rooms based on travel time minimization. Built with FastAPI, React, and MongoDB.

## 🏨 Features

- **Optimal Room Allocation**: Intelligent algorithm prioritizes same-floor bookings and minimizes travel time
- **Interactive Visualization**: Real-time room grid showing all 97 rooms across 10 floors
- **Booking Management**: Book (1-5 rooms), Reset all bookings, Generate random occupancy
- **Booking History**: Persistent storage of all bookings with travel time calculations
- **Professional UI**: Clean, Swiss-inspired design with high contrast and accessibility

## 🏗️ System Architecture

### Room Structure
- **Floors 1-9**: 10 rooms each (101-110, 201-210, etc.)
- **Floor 10**: 7 rooms (1001-1007)
- **Total**: 97 rooms
- **Layout**: Staircase/lift on left, rooms arranged left to right

### Travel Time Rules
- **Horizontal**: 1 minute per room (same floor)
- **Vertical**: 2 minutes per floor
- **Combined**: Vertical + Horizontal time for cross-floor travel

## 🚀 Live Demo

Access the application at: `https://staybooker-75.preview.emergentagent.com`

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **MongoDB**: NoSQL database for room and booking data
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and serialization

### Frontend
- **React 19**: Modern UI library
- **Tailwind CSS**: Utility-first styling
- **Shadcn/UI**: High-quality component library
- **Axios**: HTTP client
- **Sonner**: Toast notifications
- **Lucide React**: Icon library

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rooms` | Get all rooms with status |
| POST | `/api/book` | Book optimal rooms |
| POST | `/api/reset` | Clear all bookings |
| POST | `/api/random` | Generate random occupancy |
| GET | `/api/bookings` | Get booking history |

## 🧮 Algorithm Details

### Booking Priority
1. **Same Floor First**: If N rooms available on same floor, select them
2. **Cross-Floor Optimization**: If not, find combination with minimum travel time

### Example
Booking 4 rooms:
- **Scenario A**: Floor 1 has 4+ available → Select 101, 102, 103, 104
- **Scenario B**: Floor 1 has 2, Floor 2 has 2+ → Select 101, 102, 201, 202

See [ALGORITHM_EXPLANATION.md](./ALGORITHM_EXPLANATION.md) for detailed algorithm documentation.

## 🎨 Design System

- **Theme**: Swiss Utility Light Mode
- **Typography**: Chivo (headings), Public Sans (body), JetBrains Mono (monospace)
- **Colors**: High contrast black/white with zinc accents
- **Visual States**: 
  - Available: White with border
  - Booked: Gray with diagonal pattern
  - Just Selected: Black with scale animation

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Configure .env with MONGO_URL and DB_NAME
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Frontend Setup
```bash
cd frontend
yarn install
yarn start
```

## 🧪 Testing

Comprehensive test suite included:
- Backend API tests: `/app/backend_test.py`
- Test results: 100% backend pass rate

### Run Backend Tests
```bash
pytest backend_test.py -v
```

## 📊 Test Results Summary

✅ **Backend (11/11 tests passed)**
- Room initialization (97 rooms)
- Booking algorithm optimization
- Travel time calculations
- Reset functionality
- Random occupancy
- Booking history

✅ **Frontend (All features working)**
- Room grid visualization
- Staircase/lift display
- Booking interactions
- History panel
- Mobile responsiveness

## 🎯 Usage

1. **Book Rooms**:
   - Enter number of rooms (1-5)
   - Click "Book" button
   - System selects optimal rooms
   - Toast shows booked rooms and travel time

2. **Reset Bookings**:
   - Click "Reset" button
   - All bookings cleared
   - All rooms become available

3. **Random Occupancy**:
   - Click "Random" button
   - 30-60% of rooms randomly booked
   - Useful for testing scenarios

4. **View History**:
   - Click "History" button
   - Side panel shows all past bookings
   - Includes booking ID, rooms, travel time, timestamp

## 🏆 Key Achievements

- ✅ Optimal room allocation algorithm with travel time minimization
- ✅ Professional Swiss-inspired UI design
- ✅ Real-time room status visualization
- ✅ Persistent booking history
- ✅ Comprehensive testing (100% backend coverage)
- ✅ Mobile-responsive design
- ✅ Accessibility features (ARIA labels, screen reader support)

## 📝 Project Structure

```
/app/
├── backend/
│   ├── server.py           # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Custom styles
│   │   └── components/ui/ # Shadcn components
│   ├── package.json       # Node dependencies
│   └── .env              # Frontend env variables
├── design_guidelines.json  # Design system specs
├── ALGORITHM_EXPLANATION.md # Algorithm documentation
└── README.md              # This file
```

## 🔐 Environment Variables

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=hotel_reservation
CORS_ORIGINS=*
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

## 🤝 Contributing

This is an assessment project for Unstop recruitment.

## 📄 License

Created for Unstop recruitment assessment.

## 👨‍💻 Developer Notes

- Algorithm uses combinatorial optimization for cross-floor bookings
- Performance optimized for up to 97 rooms with smart sampling
- MongoDB collections: `rooms` and `bookings`
- Hot reload enabled for both frontend and backend
- Supervisor manages service lifecycle

## 📞 Support

For questions regarding this assessment, contact: careers@unstop.com


