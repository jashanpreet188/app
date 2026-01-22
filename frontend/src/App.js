import { useState, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import { toast, Toaster } from "sonner";
import { Shuffle, RotateCcw, History, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [rooms, setRooms] = useState([]);
  const [numRooms, setNumRooms] = useState(1);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastBookedRooms, setLastBookedRooms] = useState([]);

  useEffect(() => {
    fetchRooms();
    fetchBookings();
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await axios.get(`${API}/rooms`);
      setRooms(response.data.rooms);
    } catch (error) {
      console.error("Error fetching rooms:", error);
      toast.error("Failed to load rooms");
    }
  };

  const fetchBookings = async () => {
    try {
      const response = await axios.get(`${API}/bookings`);
      setBookings(response.data.bookings);
    } catch (error) {
      console.error("Error fetching bookings:", error);
    }
  };

  const handleBook = async () => {
    if (!numRooms || isNaN(numRooms) || numRooms < 1 || numRooms > 5) {
      toast.error("Please enter a valid number between 1 and 5");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/book`, { num_rooms: numRooms });
      toast.success(`Booked ${response.data.rooms.length} rooms! Travel time: ${response.data.total_travel_time.toFixed(1)} min`);
      setLastBookedRooms(response.data.rooms);
      await fetchRooms();
      await fetchBookings();
      
      // Clear highlight after 3 seconds
      setTimeout(() => setLastBookedRooms([]), 3000);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || "Failed to book rooms";
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/reset`);
      toast.success("All bookings cleared");
      setLastBookedRooms([]);
      await fetchRooms();
      await fetchBookings();
    } catch (error) {
      toast.error("Failed to reset bookings");
    } finally {
      setLoading(false);
    }
  };

  const handleRandom = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/random`);
      toast.success(`Generated random occupancy: ${response.data.rooms_booked} rooms booked`);
      setLastBookedRooms([]);
      await fetchRooms();
    } catch (error) {
      toast.error("Failed to generate random occupancy");
    } finally {
      setLoading(false);
    }
  };

  // Group rooms by floor
  const roomsByFloor = {};
  rooms.forEach(room => {
    if (!roomsByFloor[room.floor]) {
      roomsByFloor[room.floor] = [];
    }
    roomsByFloor[room.floor].push(room);
  });

  const getRoomStyle = (room) => {
    if (lastBookedRooms.includes(room.room_number)) {
      return "room-selected";
    }
    if (room.is_booked) {
      return "room-booked";
    }
    return "room-available";
  };

  return (
    <div className="app-container">
      <Toaster position="top-center" richColors />
      
      {/* Control Panel */}
      <div className="control-panel">
        <div className="control-left">
          <Building2 className="w-6 h-6" />
          <h1 className="text-2xl font-black tracking-tight">Hotel Room Reservation</h1>
        </div>
        
        <div className="control-actions">
          <div className="input-group">
            <label htmlFor="num-rooms" className="input-label">No of Rooms</label>
            <Input
              id="num-rooms"
              data-testid="num-rooms-input"
              type="number"
              min="1"
              max="5"
              value={numRooms}
              onChange={(e) => setNumRooms(parseInt(e.target.value) || 1)}
              className="w-24"
            />
          </div>
          
          <Button
            data-testid="book-btn"
            onClick={handleBook}
            disabled={loading}
            className="btn-primary"
          >
            Book
          </Button>
          
          <Button
            data-testid="reset-btn"
            onClick={handleReset}
            disabled={loading}
            variant="outline"
            className="btn-outline"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          
          <Button
            data-testid="random-btn"
            onClick={handleRandom}
            disabled={loading}
            variant="outline"
            className="btn-outline"
          >
            <Shuffle className="w-4 h-4 mr-2" />
            Random
          </Button>
          
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" className="btn-outline">
                <History className="w-4 h-4 mr-2" />
                History
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>Booking History</SheetTitle>
              </SheetHeader>
              <ScrollArea className="h-[calc(100vh-120px)] mt-6">
                {bookings.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No bookings yet</p>
                ) : (
                  <div className="space-y-4">
                    {bookings.map((booking, idx) => (
                      <div key={idx} className="booking-card">
                        <div className="booking-id">{booking.booking_id}</div>
                        <div className="booking-detail">
                          <span className="detail-label">Rooms:</span>
                          <span className="detail-value">{booking.rooms.join(", ")}</span>
                        </div>
                        <div className="booking-detail">
                          <span className="detail-label">Travel Time:</span>
                          <span className="detail-value">{booking.total_travel_time.toFixed(1)} min</span>
                        </div>
                        <div className="booking-time">
                          {new Date(booking.created_at).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </SheetContent>
          </Sheet>
        </div>
      </div>

      {/* Main Layout: Staircase + Rooms */}
      <div className="main-layout">
        {/* Staircase/Lift Column */}
        <div className="staircase-column">
          <div className="staircase-label">STAIRS / LIFT</div>
        </div>

        {/* Room Grid */}
        <div className="room-grid-container">
          {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map(floor => (
            <div key={floor} className="floor-row">
              <div className="floor-label">F{floor}</div>
              <div className="rooms-row">
                {roomsByFloor[floor]?.map(room => (
                  <div
                    key={room.room_number}
                    data-testid={`room-${room.room_number}`}
                    className={`room-cell ${getRoomStyle(room)}`}
                    title={`Room ${room.room_number} - ${room.is_booked ? 'Booked' : 'Available'}`}
                  >
                    {room.room_number}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="legend">
        <div className="legend-item">
          <div className="legend-box room-available"></div>
          <span>Available</span>
        </div>
        <div className="legend-item">
          <div className="legend-box room-booked"></div>
          <span>Booked</span>
        </div>
        <div className="legend-item">
          <div className="legend-box room-selected"></div>
          <span>Just Selected</span>
        </div>
      </div>
    </div>
  );
}

export default App;