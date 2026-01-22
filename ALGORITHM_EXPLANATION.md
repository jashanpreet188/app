# Hotel Room Reservation Algorithm

## Overview
This algorithm optimally selects hotel rooms to minimize total travel time between booked rooms, following the specified priority rules.

## Room Structure
- **Floors 1-9**: 10 rooms each (101-110, 201-210, ..., 901-910)
- **Floor 10**: 7 rooms (1001-1007)
- **Total**: 97 rooms
- **Staircase/Lift**: Located on the left side of building

## Travel Time Calculation
1. **Horizontal travel** (same floor): 1 minute per room
   - Example: Room 101 to 103 = |1 - 3| × 1 = 2 minutes
   
2. **Vertical travel** (different floors): 2 minutes per floor + horizontal distance
   - Example: Room 201 to 305 = |2 - 3| × 2 + |1 - 5| × 1 = 4 + 4 = 8 minutes

## Algorithm Logic

### Priority 1: Same Floor Selection
When requesting N rooms:
1. Group all available rooms by floor
2. Check if any single floor has ≥ N available rooms
3. If yes, select N consecutive or nearest rooms from that floor
4. Calculate travel time: distance between first and last room

**Example**: Booking 4 rooms with Floor 1 available (101, 102, 105, 106)
- Selected: 101, 102, 105, 106
- Travel time: 3 × 1 = 3 minutes

### Priority 2: Cross-Floor Optimization
If no single floor has enough rooms:
1. Generate all possible combinations of N rooms from available rooms
2. For each combination:
   - Sort rooms by (floor, position)
   - Calculate total travel time between consecutive rooms
3. Select combination with minimum total travel time

**Example**: Booking 4 rooms
- Available: Floor 1 (101, 102), Floor 2 (201, 202, 203)
- Possible combinations evaluated for minimum travel time
- Best combination selected

### Performance Optimization
- If available rooms > 30: Use random sampling (1000 combinations) instead of exhaustive search
- Prevents exponential complexity with large datasets
- Still provides near-optimal results

## API Endpoints

### 1. GET /api/rooms
Returns all 97 rooms with status
```json
{
  "rooms": [
    {
      "room_number": 101,
      "floor": 1,
      "position": 1,
      "is_booked": false,
      "booked_at": null
    }
  ]
}
```

### 2. POST /api/book
Books optimal rooms
```json
// Request
{
  "num_rooms": 3
}

// Response
{
  "booking_id": "BK1737563242123",
  "rooms": [101, 102, 103],
  "total_travel_time": 2.0,
  "created_at": "2025-01-22T15:30:42.123Z"
}
```

### 3. POST /api/reset
Clears all bookings

### 4. POST /api/random
Generates random occupancy (30-60% of rooms)

### 5. GET /api/bookings
Returns booking history

## Edge Cases Handled

1. **Insufficient rooms**: Returns 400 error if not enough rooms available
2. **Invalid input**: Validates 1 ≤ num_rooms ≤ 5
3. **All rooms on one floor**: Prioritizes same-floor selection
4. **Scattered availability**: Finds optimal cross-floor combination
5. **Performance**: Handles large available room sets efficiently

## Example Scenarios

### Scenario 1: Optimal Same-Floor
- Request: 4 rooms
- Available: Floor 1 (101-110 all available)
- Result: 101, 102, 103, 104
- Travel time: 3 minutes

### Scenario 2: Cross-Floor Optimization
- Request: 4 rooms
- Available: Floor 1 (101, 102), Floor 2 (201, 202, 210)
- Algorithm evaluates all combinations:
  - [101, 102, 201, 202]: Travel = 1 + 2 + 1 = 4 minutes ✓ BEST
  - [101, 102, 201, 210]: Travel = 1 + 2 + 9 = 12 minutes
  - [101, 201, 202, 210]: Travel = 2 + 1 + 9 = 12 minutes
- Result: 101, 102, 201, 202
- Travel time: 4 minutes

## Database Schema

### rooms collection
```javascript
{
  room_number: 101,
  floor: 1,
  position: 1,
  is_booked: false,
  booked_at: "2025-01-22T15:30:42.123Z" | null
}
```

### bookings collection
```javascript
{
  booking_id: "BK1737563242123",
  rooms: [101, 102, 103],
  total_travel_time: 2.0,
  created_at: "2025-01-22T15:30:42.123Z"
}
```

## Testing Results
- ✅ All 97 rooms correctly initialized
- ✅ Same-floor priority working correctly
- ✅ Cross-floor optimization functioning
- ✅ Travel time calculations accurate
- ✅ Booking history persisted correctly
- ✅ Reset and random occupancy working
- ✅ Frontend visualization matches backend state
