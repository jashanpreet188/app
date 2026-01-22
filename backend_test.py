import requests
import sys
import json
from datetime import datetime

class HotelReservationTester:
    def __init__(self, base_url="https://staybooker-75.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_get_rooms(self):
        """Test room initialization - verify all 97 rooms exist"""
        try:
            response = requests.get(f"{self.api_url}/rooms", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Get Rooms API", False, f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            rooms = data.get('rooms', [])
            
            # Check total room count
            if len(rooms) != 97:
                self.log_test("Room Count", False, f"Expected 97 rooms, got {len(rooms)}")
                return False
            
            # Check floor structure
            floor_counts = {}
            for room in rooms:
                floor = room['floor']
                floor_counts[floor] = floor_counts.get(floor, 0) + 1
            
            # Verify floor 1-9 have 10 rooms each
            for floor in range(1, 10):
                if floor_counts.get(floor, 0) != 10:
                    self.log_test("Floor Structure", False, f"Floor {floor} has {floor_counts.get(floor, 0)} rooms, expected 10")
                    return False
            
            # Verify floor 10 has 7 rooms
            if floor_counts.get(10, 0) != 7:
                self.log_test("Floor 10 Structure", False, f"Floor 10 has {floor_counts.get(10, 0)} rooms, expected 7")
                return False
            
            # Check room number format
            expected_rooms = []
            # Floors 1-9
            for floor in range(1, 10):
                for pos in range(1, 11):
                    expected_rooms.append(floor * 100 + pos)
            # Floor 10
            for pos in range(1, 8):
                expected_rooms.append(1000 + pos)
            
            actual_rooms = [room['room_number'] for room in rooms]
            actual_rooms.sort()
            expected_rooms.sort()
            
            if actual_rooms != expected_rooms:
                self.log_test("Room Numbers", False, "Room numbers don't match expected format")
                return False
            
            self.log_test("Room Initialization", True, f"All 97 rooms correctly initialized")
            return True
            
        except Exception as e:
            self.log_test("Get Rooms API", False, f"Exception: {str(e)}")
            return False

    def test_booking_algorithm(self):
        """Test booking algorithm with various scenarios"""
        try:
            # First reset all bookings
            reset_response = requests.post(f"{self.api_url}/reset", timeout=10)
            if reset_response.status_code != 200:
                self.log_test("Reset for Booking Test", False, f"Reset failed: {reset_response.status_code}")
                return False
            
            # Test 1: Book 1 room
            response = requests.post(f"{self.api_url}/book", json={"num_rooms": 1}, timeout=10)
            if response.status_code != 200:
                self.log_test("Book 1 Room", False, f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            if len(data['rooms']) != 1:
                self.log_test("Book 1 Room", False, f"Expected 1 room, got {len(data['rooms'])}")
                return False
            
            self.log_test("Book 1 Room", True, f"Booked room {data['rooms'][0]} with travel time {data['total_travel_time']}")
            
            # Test 2: Book 3 rooms (should prioritize same floor)
            response = requests.post(f"{self.api_url}/book", json={"num_rooms": 3}, timeout=10)
            if response.status_code != 200:
                self.log_test("Book 3 Rooms", False, f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            if len(data['rooms']) != 3:
                self.log_test("Book 3 Rooms", False, f"Expected 3 rooms, got {len(data['rooms'])}")
                return False
            
            # Check if rooms are on same floor (optimal)
            floors = [int(str(room)[:1]) if room < 1000 else 10 for room in data['rooms']]
            same_floor = len(set(floors)) == 1
            
            self.log_test("Book 3 Rooms", True, f"Booked rooms {data['rooms']} (same floor: {same_floor}) with travel time {data['total_travel_time']}")
            
            # Test 3: Book 5 rooms (maximum)
            response = requests.post(f"{self.api_url}/book", json={"num_rooms": 5}, timeout=10)
            if response.status_code != 200:
                self.log_test("Book 5 Rooms", False, f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            if len(data['rooms']) != 5:
                self.log_test("Book 5 Rooms", False, f"Expected 5 rooms, got {len(data['rooms'])}")
                return False
            
            self.log_test("Book 5 Rooms", True, f"Booked 5 rooms with travel time {data['total_travel_time']}")
            
            # Test 4: Invalid booking (more than 5 rooms)
            response = requests.post(f"{self.api_url}/book", json={"num_rooms": 6}, timeout=10)
            if response.status_code == 422:  # Validation error
                self.log_test("Invalid Booking (>5 rooms)", True, "Correctly rejected booking >5 rooms")
            else:
                self.log_test("Invalid Booking (>5 rooms)", False, f"Should reject >5 rooms, got status: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Booking Algorithm", False, f"Exception: {str(e)}")
            return False

    def test_reset_functionality(self):
        """Test reset functionality"""
        try:
            # First book some rooms
            requests.post(f"{self.api_url}/book", json={"num_rooms": 3}, timeout=10)
            
            # Reset all bookings
            response = requests.post(f"{self.api_url}/reset", timeout=10)
            if response.status_code != 200:
                self.log_test("Reset Bookings", False, f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            if 'rooms_reset' not in data:
                self.log_test("Reset Response", False, "Missing rooms_reset in response")
                return False
            
            # Verify all rooms are available
            rooms_response = requests.get(f"{self.api_url}/rooms", timeout=10)
            rooms_data = rooms_response.json()
            booked_rooms = [room for room in rooms_data['rooms'] if room['is_booked']]
            
            if len(booked_rooms) > 0:
                self.log_test("Reset Verification", False, f"Found {len(booked_rooms)} still booked after reset")
                return False
            
            self.log_test("Reset Functionality", True, f"Reset {data['rooms_reset']} rooms successfully")
            return True
            
        except Exception as e:
            self.log_test("Reset Functionality", False, f"Exception: {str(e)}")
            return False

    def test_random_occupancy(self):
        """Test random occupancy generation"""
        try:
            response = requests.post(f"{self.api_url}/random", timeout=10)
            if response.status_code != 200:
                self.log_test("Random Occupancy", False, f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            rooms_booked = data.get('rooms_booked', 0)
            
            # Should book 30-60% of 97 rooms (29-58 rooms)
            if rooms_booked < 29 or rooms_booked > 58:
                self.log_test("Random Occupancy Range", False, f"Booked {rooms_booked} rooms, expected 29-58")
                return False
            
            # Verify actual room status
            rooms_response = requests.get(f"{self.api_url}/rooms", timeout=10)
            rooms_data = rooms_response.json()
            actual_booked = len([room for room in rooms_data['rooms'] if room['is_booked']])
            
            if actual_booked != rooms_booked:
                self.log_test("Random Occupancy Verification", False, f"API says {rooms_booked} booked, but found {actual_booked}")
                return False
            
            self.log_test("Random Occupancy", True, f"Generated {rooms_booked} random bookings")
            return True
            
        except Exception as e:
            self.log_test("Random Occupancy", False, f"Exception: {str(e)}")
            return False

    def test_booking_history(self):
        """Test booking history functionality"""
        try:
            # Reset and make a booking
            requests.post(f"{self.api_url}/reset", timeout=10)
            booking_response = requests.post(f"{self.api_url}/book", json={"num_rooms": 2}, timeout=10)
            
            if booking_response.status_code != 200:
                self.log_test("Booking for History", False, "Failed to create booking for history test")
                return False
            
            booking_data = booking_response.json()
            booking_id = booking_data['booking_id']
            
            # Get booking history
            response = requests.get(f"{self.api_url}/bookings", timeout=10)
            if response.status_code != 200:
                self.log_test("Get Booking History", False, f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            bookings = data.get('bookings', [])
            
            if len(bookings) == 0:
                self.log_test("Booking History", False, "No bookings found in history")
                return False
            
            # Find our booking
            our_booking = None
            for booking in bookings:
                if booking['booking_id'] == booking_id:
                    our_booking = booking
                    break
            
            if not our_booking:
                self.log_test("Booking History", False, f"Booking {booking_id} not found in history")
                return False
            
            # Verify booking data
            required_fields = ['booking_id', 'rooms', 'total_travel_time', 'created_at']
            for field in required_fields:
                if field not in our_booking:
                    self.log_test("Booking History Fields", False, f"Missing field: {field}")
                    return False
            
            self.log_test("Booking History", True, f"Found booking {booking_id} with {len(our_booking['rooms'])} rooms")
            return True
            
        except Exception as e:
            self.log_test("Booking History", False, f"Exception: {str(e)}")
            return False

    def test_travel_time_calculation(self):
        """Test travel time calculation accuracy"""
        try:
            # Reset and book rooms on same floor
            requests.post(f"{self.api_url}/reset", timeout=10)
            
            # Book 2 rooms - should get consecutive rooms on same floor with minimal travel time
            response = requests.post(f"{self.api_url}/book", json={"num_rooms": 2}, timeout=10)
            if response.status_code != 200:
                self.log_test("Travel Time Test Setup", False, "Failed to book rooms for travel time test")
                return False
            
            data = response.json()
            rooms = data['rooms']
            travel_time = data['total_travel_time']
            
            # For 2 consecutive rooms on same floor, travel time should be 1.0 minute
            # For rooms on different floors, it should be higher
            if len(rooms) == 2:
                room1_floor = int(str(rooms[0])[:1]) if rooms[0] < 1000 else 10
                room2_floor = int(str(rooms[1])[:1]) if rooms[1] < 1000 else 10
                
                if room1_floor == room2_floor:
                    # Same floor - should be horizontal distance only
                    room1_pos = rooms[0] % 100 if rooms[0] < 1000 else rooms[0] % 10
                    room2_pos = rooms[1] % 100 if rooms[1] < 1000 else rooms[1] % 10
                    expected_time = abs(room1_pos - room2_pos) * 1.0
                    
                    if abs(travel_time - expected_time) > 0.1:  # Allow small floating point differences
                        self.log_test("Travel Time Calculation", False, f"Expected {expected_time}, got {travel_time}")
                        return False
                else:
                    # Different floors - should include vertical time
                    if travel_time < 2.0:  # At least 2 minutes for different floors
                        self.log_test("Travel Time Calculation", False, f"Cross-floor travel time too low: {travel_time}")
                        return False
            
            self.log_test("Travel Time Calculation", True, f"Travel time {travel_time} min for rooms {rooms}")
            return True
            
        except Exception as e:
            self.log_test("Travel Time Calculation", False, f"Exception: {str(e)}")
            return False

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        try:
            # Test booking when no rooms available
            requests.post(f"{self.api_url}/reset", timeout=10)
            
            # Book all available rooms in small batches to avoid timeout
            total_booked = 0
            while total_booked < 97:
                remaining = 97 - total_booked
                batch_size = min(5, remaining)
                
                response = requests.post(f"{self.api_url}/book", json={"num_rooms": batch_size}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    total_booked += len(data['rooms'])
                else:
                    break
            
            # Now try to book one more room - should fail
            response = requests.post(f"{self.api_url}/book", json={"num_rooms": 1}, timeout=10)
            if response.status_code == 400:
                self.log_test("No Rooms Available", True, "Correctly rejected booking when no rooms available")
            else:
                self.log_test("No Rooms Available", False, f"Should reject when no rooms available, got: {response.status_code}")
            
            # Test invalid input
            response = requests.post(f"{self.api_url}/book", json={"num_rooms": 0}, timeout=10)
            if response.status_code == 422:
                self.log_test("Invalid Input (0 rooms)", True, "Correctly rejected 0 rooms")
            else:
                self.log_test("Invalid Input (0 rooms)", False, f"Should reject 0 rooms, got: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Edge Cases", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🏨 Starting Hotel Reservation System Backend Tests")
        print("=" * 60)
        
        # Test sequence
        self.test_get_rooms()
        self.test_booking_algorithm()
        self.test_reset_functionality()
        self.test_random_occupancy()
        self.test_booking_history()
        self.test_travel_time_calculation()
        self.test_edge_cases()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Backend Tests Summary: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All backend tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = HotelReservationTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())