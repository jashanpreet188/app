from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
from itertools import combinations
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class Room(BaseModel):
    model_config = ConfigDict(extra="ignore")
    room_number: int
    floor: int
    position: int
    is_booked: bool = False
    booked_at: Optional[str] = None

class BookingRequest(BaseModel):
    num_rooms: int = Field(..., ge=1, le=5)

class BookingResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    booking_id: str
    rooms: List[int]
    total_travel_time: float
    created_at: str

# Room initialization
def generate_all_rooms():
    rooms = []
    # Floors 1-9: 10 rooms each
    for floor in range(1, 10):
        for pos in range(1, 11):
            room_number = floor * 100 + pos
            rooms.append({
                "room_number": room_number,
                "floor": floor,
                "position": pos,
                "is_booked": False,
                "booked_at": None
            })
    
    # Floor 10: 7 rooms
    for pos in range(1, 8):
        room_number = 1000 + pos
        rooms.append({
            "room_number": room_number,
            "floor": 10,
            "position": pos,
            "is_booked": False,
            "booked_at": None
        })
    
    return rooms

# Travel time calculation
def calculate_travel_time(room1: dict, room2: dict) -> float:
    if room1['floor'] == room2['floor']:
        return abs(room1['position'] - room2['position']) * 1.0
    else:
        vertical_time = abs(room1['floor'] - room2['floor']) * 2.0
        horizontal_time = abs(room1['position'] - room2['position']) * 1.0
        return vertical_time + horizontal_time

# Calculate total travel time for a combination of rooms
def calculate_total_travel_time(rooms: List[dict]) -> float:
    if len(rooms) <= 1:
        return 0.0
    
    total_time = 0.0
    for i in range(len(rooms) - 1):
        total_time += calculate_travel_time(rooms[i], rooms[i + 1])
    
    return total_time

# Optimal room selection algorithm
def select_optimal_rooms(available_rooms: List[dict], num_rooms: int) -> tuple[List[dict], float]:
    if len(available_rooms) < num_rooms:
        raise ValueError("Not enough available rooms")
    
    # Group rooms by floor
    floors = {}
    for room in available_rooms:
        floor = room['floor']
        if floor not in floors:
            floors[floor] = []
        floors[floor].append(room)
    
    # Priority 1: Try to find rooms on the same floor
    for floor, rooms_on_floor in floors.items():
        if len(rooms_on_floor) >= num_rooms:
            # Sort by position to get consecutive or nearest rooms
            rooms_on_floor.sort(key=lambda x: x['position'])
            selected = rooms_on_floor[:num_rooms]
            travel_time = calculate_total_travel_time(selected)
            return selected, travel_time
    
    # Priority 2: Find combination across floors with minimum travel time
    best_combination = None
    min_travel_time = float('inf')
    
    # Limit combinations for performance (if too many rooms available)
    if len(available_rooms) > 30:
        # Sample random combinations
        for _ in range(min(1000, len(list(combinations(range(len(available_rooms)), num_rooms))))):
            indices = random.sample(range(len(available_rooms)), num_rooms)
            combo = [available_rooms[i] for i in sorted(indices)]
            combo.sort(key=lambda x: (x['floor'], x['position']))
            travel_time = calculate_total_travel_time(combo)
            
            if travel_time < min_travel_time:
                min_travel_time = travel_time
                best_combination = combo
    else:
        # Check all combinations
        for combo_indices in combinations(range(len(available_rooms)), num_rooms):
            combo = [available_rooms[i] for i in combo_indices]
            combo.sort(key=lambda x: (x['floor'], x['position']))
            travel_time = calculate_total_travel_time(combo)
            
            if travel_time < min_travel_time:
                min_travel_time = travel_time
                best_combination = combo
    
    return best_combination, min_travel_time

# Initialize rooms on startup
@app.on_event("startup")
async def initialize_db():
    count = await db.rooms.count_documents({})
    if count == 0:
        rooms = generate_all_rooms()
        await db.rooms.insert_many(rooms)
        logger.info("Initialized 97 rooms in database")

# API Routes
@api_router.get("/rooms")
async def get_rooms():
    rooms = await db.rooms.find({}, {"_id": 0}).sort("room_number", 1).to_list(100)
    return {"rooms": rooms}

@api_router.post("/book")
async def book_rooms(request: BookingRequest):
    # Get available rooms
    available_rooms = await db.rooms.find({"is_booked": False}, {"_id": 0}).to_list(100)
    
    if len(available_rooms) < request.num_rooms:
        raise HTTPException(status_code=400, detail=f"Only {len(available_rooms)} rooms available")
    
    try:
        selected_rooms, travel_time = select_optimal_rooms(available_rooms, request.num_rooms)
        
        # Update room status
        room_numbers = [room['room_number'] for room in selected_rooms]
        timestamp = datetime.now(timezone.utc).isoformat()
        
        await db.rooms.update_many(
            {"room_number": {"$in": room_numbers}},
            {"$set": {"is_booked": True, "booked_at": timestamp}}
        )
        
        # Save booking history
        booking_id = f"BK{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        booking_doc = {
            "booking_id": booking_id,
            "rooms": room_numbers,
            "total_travel_time": travel_time,
            "created_at": timestamp
        }
        await db.bookings.insert_one(booking_doc)
        
        return {
            "booking_id": booking_id,
            "rooms": room_numbers,
            "total_travel_time": travel_time,
            "created_at": timestamp,
            "message": "Rooms booked successfully"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/reset")
async def reset_bookings():
    result = await db.rooms.update_many(
        {},
        {"$set": {"is_booked": False, "booked_at": None}}
    )
    
    return {
        "message": "All bookings cleared",
        "rooms_reset": result.modified_count
    }

@api_router.post("/random")
async def random_occupancy():
    all_rooms = await db.rooms.find({}, {"_id": 0}).to_list(100)
    
    # Reset all first
    await db.rooms.update_many({}, {"$set": {"is_booked": False, "booked_at": None}})
    
    # Randomly book 30-60% of rooms
    num_to_book = random.randint(30, 58)
    rooms_to_book = random.sample(all_rooms, num_to_book)
    room_numbers = [room['room_number'] for room in rooms_to_book]
    
    timestamp = datetime.now(timezone.utc).isoformat()
    await db.rooms.update_many(
        {"room_number": {"$in": room_numbers}},
        {"$set": {"is_booked": True, "booked_at": timestamp}}
    )
    
    return {
        "message": "Random occupancy generated",
        "rooms_booked": len(room_numbers)
    }

@api_router.get("/bookings")
async def get_bookings():
    bookings = await db.bookings.find({}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    return {"bookings": bookings}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()