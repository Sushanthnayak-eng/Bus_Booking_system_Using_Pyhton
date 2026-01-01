"""
Bus Booking System
A simple console-based bus booking system for managing bus reservations.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Bus:
    """Represents a bus with its details and seat availability."""
    
    def __init__(self, bus_id: str, bus_name: str, total_seats: int, fare: float):
        self.bus_id = bus_id
        self.bus_name = bus_name
        self.total_seats = total_seats
        self.fare = fare
        self.available_seats = total_seats
        self.booked_seats: List[int] = []
    
    def book_seat(self, seat_number: int) -> bool:
        """Book a specific seat if available."""
        if seat_number < 1 or seat_number > self.total_seats:
            return False
        if seat_number in self.booked_seats:
            return False
        self.booked_seats.append(seat_number)
        self.available_seats -= 1
        return True
    
    def cancel_seat(self, seat_number: int) -> bool:
        """Cancel a booked seat."""
        if seat_number in self.booked_seats:
            self.booked_seats.remove(seat_number)
            self.available_seats += 1
            return True
        return False
    
    def to_dict(self) -> dict:
        """Convert bus object to dictionary for serialization."""
        return {
            'bus_id': self.bus_id,
            'bus_name': self.bus_name,
            'total_seats': self.total_seats,
            'fare': self.fare,
            'available_seats': self.available_seats,
            'booked_seats': self.booked_seats
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Bus':
        """Create bus object from dictionary."""
        bus = Bus(data['bus_id'], data['bus_name'], data['total_seats'], data['fare'])
        bus.available_seats = data['available_seats']
        bus.booked_seats = data['booked_seats']
        return bus


class Route:
    """Represents a bus route with source and destination."""
    
    def __init__(self, route_id: str, source: str, destination: str, distance_km: float):
        self.route_id = route_id
        self.source = source
        self.destination = destination
        self.distance_km = distance_km
        self.buses: List[Bus] = []
    
    def add_bus(self, bus: Bus) -> None:
        """Add a bus to this route."""
        self.buses.append(bus)
    
    def get_available_buses(self) -> List[Bus]:
        """Get list of buses with available seats on this route."""
        return [bus for bus in self.buses if bus.available_seats > 0]
    
    def to_dict(self) -> dict:
        """Convert route object to dictionary for serialization."""
        return {
            'route_id': self.route_id,
            'source': self.source,
            'destination': self.destination,
            'distance_km': self.distance_km,
            'buses': [bus.to_dict() for bus in self.buses]
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Route':
        """Create route object from dictionary."""
        route = Route(data['route_id'], data['source'], data['destination'], data['distance_km'])
        route.buses = [Bus.from_dict(bus_data) for bus_data in data['buses']]
        return route


class Booking:
    """Represents a booking made by a passenger."""
    
    def __init__(self, booking_id: str, passenger_name: str, passenger_phone: str,
                 bus_id: str, route_id: str, seat_number: int, fare: float):
        self.booking_id = booking_id
        self.passenger_name = passenger_name
        self.passenger_phone = passenger_phone
        self.bus_id = bus_id
        self.route_id = route_id
        self.seat_number = seat_number
        self.fare = fare
        self.booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "CONFIRMED"
    
    def to_dict(self) -> dict:
        """Convert booking object to dictionary for serialization."""
        return {
            'booking_id': self.booking_id,
            'passenger_name': self.passenger_name,
            'passenger_phone': self.passenger_phone,
            'bus_id': self.bus_id,
            'route_id': self.route_id,
            'seat_number': self.seat_number,
            'fare': self.fare,
            'booking_date': self.booking_date,
            'status': self.status
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Booking':
        """Create booking object from dictionary."""
        booking = Booking(
            data['booking_id'], data['passenger_name'], data['passenger_phone'],
            data['bus_id'], data['route_id'], data['seat_number'], data['fare']
        )
        booking.booking_date = data['booking_date']
        booking.status = data['status']
        return booking


class BusBookingSystem:
    """Main bus booking system class."""
    
    def __init__(self, data_file: str = "booking_data.json"):
        self.routes: Dict[str, Route] = {}
        self.bookings: Dict[str, Booking] = {}
        self.data_file = data_file
        self.booking_counter = 1
        self.load_data()
    
    def add_route(self, route_id: str, source: str, destination: str, distance_km: float) -> Route:
        """Add a new route to the system."""
        route = Route(route_id, source, destination, distance_km)
        self.routes[route_id] = route
        return route
    
    def add_bus_to_route(self, route_id: str, bus_id: str, bus_name: str, 
                        total_seats: int, fare: float) -> Optional[Bus]:
        """Add a bus to a specific route."""
        if route_id not in self.routes:
            return None
        bus = Bus(bus_id, bus_name, total_seats, fare)
        self.routes[route_id].add_bus(bus)
        return bus
    
    def search_routes(self, source: str, destination: str) -> List[Route]:
        """Search for routes between source and destination."""
        matching_routes = []
        for route in self.routes.values():
            if route.source.lower() == source.lower() and route.destination.lower() == destination.lower():
                matching_routes.append(route)
        return matching_routes
    
    def create_booking(self, passenger_name: str, passenger_phone: str, 
                      route_id: str, bus_id: str, seat_number: int) -> Optional[Booking]:
        """Create a new booking."""
        if route_id not in self.routes:
            return None
        
        route = self.routes[route_id]
        bus = None
        for b in route.buses:
            if b.bus_id == bus_id:
                bus = b
                break
        
        if not bus:
            return None
        
        if not bus.book_seat(seat_number):
            return None
        
        booking_id = f"BK{self.booking_counter:04d}"
        self.booking_counter += 1
        
        booking = Booking(booking_id, passenger_name, passenger_phone, 
                         bus_id, route_id, seat_number, bus.fare)
        self.bookings[booking_id] = booking
        self.save_data()
        return booking
    
    def cancel_booking(self, booking_id: str) -> bool:
        """Cancel an existing booking."""
        if booking_id not in self.bookings:
            return False
        
        booking = self.bookings[booking_id]
        route = self.routes.get(booking.route_id)
        
        if not route:
            return False
        
        bus = None
        for b in route.buses:
            if b.bus_id == booking.bus_id:
                bus = b
                break
        
        if not bus:
            return False
        
        bus.cancel_seat(booking.seat_number)
        booking.status = "CANCELLED"
        self.save_data()
        return True
    
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Get booking details by booking ID."""
        return self.bookings.get(booking_id)
    
    def save_data(self) -> None:
        """Save all data to file."""
        data = {
            'routes': {rid: route.to_dict() for rid, route in self.routes.items()},
            'bookings': {bid: booking.to_dict() for bid, booking in self.bookings.items()},
            'booking_counter': self.booking_counter
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except (IOError, OSError, PermissionError) as e:
            print(f"\nWarning: Failed to save data to {self.data_file}: {e}")
            print("Your changes may not be persisted.")
    
    def load_data(self) -> None:
        """Load data from file if it exists."""
        if not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            self.routes = {rid: Route.from_dict(route_data) 
                          for rid, route_data in data.get('routes', {}).items()}
            self.bookings = {bid: Booking.from_dict(booking_data) 
                           for bid, booking_data in data.get('bookings', {}).items()}
            self.booking_counter = data.get('booking_counter', 1)
        except json.JSONDecodeError as e:
            print(f"Error: Booking data file is corrupted: {e}")
            print("Starting with empty database.")
        except (IOError, OSError, PermissionError) as e:
            print(f"Error: Cannot read booking data file {self.data_file}: {e}")
            print("Starting with empty database. Check file permissions.")
        except KeyError as e:
            print(f"Error: Invalid data format in booking file: {e}")
            print("Starting with empty database.")


def display_menu():
    """Display the main menu."""
    print("\n" + "="*50)
    print("       BUS BOOKING SYSTEM")
    print("="*50)
    print("1. View Available Routes")
    print("2. Search Routes")
    print("3. View Available Buses on Route")
    print("4. Book a Ticket")
    print("5. Cancel Booking")
    print("6. View Booking Details")
    print("7. Add Route (Admin)")
    print("8. Add Bus to Route (Admin)")
    print("9. Exit")
    print("="*50)


def main():
    """Main function to run the bus booking system."""
    system = BusBookingSystem()
    
    # Initialize with some sample data if the system is empty
    if not system.routes:
        print("Initializing system with sample data...")
        route1 = system.add_route("R001", "Mumbai", "Pune", 150)
        system.add_bus_to_route("R001", "B001", "Volvo AC", 40, 500)
        system.add_bus_to_route("R001", "B002", "Mercedes Sleeper", 36, 800)
        
        route2 = system.add_route("R002", "Delhi", "Jaipur", 280)
        system.add_bus_to_route("R002", "B003", "Scania Multi-Axle", 45, 600)
        
        route3 = system.add_route("R003", "Bangalore", "Mysore", 145)
        system.add_bus_to_route("R003", "B004", "Ashok Leyland AC", 40, 450)
        
        system.save_data()
        print("Sample data initialized!\n")
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == "1":
            print("\n--- Available Routes ---")
            if not system.routes:
                print("No routes available.")
            else:
                for route in system.routes.values():
                    print(f"\nRoute ID: {route.route_id}")
                    print(f"From: {route.source} To: {route.destination}")
                    print(f"Distance: {route.distance_km} km")
                    print(f"Number of Buses: {len(route.buses)}")
        
        elif choice == "2":
            source = input("Enter source city: ").strip()
            destination = input("Enter destination city: ").strip()
            
            if not source or not destination:
                print("\nSearch failed! Source and destination cannot be empty.")
                continue
            
            routes = system.search_routes(source, destination)
            
            if not routes:
                print(f"\nNo routes found from {source} to {destination}")
            else:
                print(f"\n--- Routes from {source} to {destination} ---")
                for route in routes:
                    print(f"\nRoute ID: {route.route_id}")
                    print(f"Distance: {route.distance_km} km")
                    print(f"Available Buses: {len(route.get_available_buses())}")
        
        elif choice == "3":
            route_id = input("Enter route ID: ").strip()
            if route_id not in system.routes:
                print("\nInvalid route ID!")
            else:
                route = system.routes[route_id]
                available_buses = route.get_available_buses()
                
                if not available_buses:
                    print("\nNo buses available on this route.")
                else:
                    print(f"\n--- Available Buses on Route {route_id} ---")
                    for bus in available_buses:
                        print(f"\nBus ID: {bus.bus_id}")
                        print(f"Bus Name: {bus.bus_name}")
                        print(f"Available Seats: {bus.available_seats}/{bus.total_seats}")
                        print(f"Fare: ₹{bus.fare}")
        
        elif choice == "4":
            print("\n--- Book a Ticket ---")
            route_id = input("Enter route ID: ").strip()
            if route_id not in system.routes:
                print("\nInvalid route ID!")
                continue
            
            bus_id = input("Enter bus ID: ").strip()
            seat_number = input("Enter seat number: ").strip()
            
            try:
                seat_number = int(seat_number)
            except ValueError:
                print("\nInvalid seat number!")
                continue
            
            passenger_name = input("Enter passenger name: ").strip()
            passenger_phone = input("Enter phone number: ").strip()
            
            if not passenger_name:
                print("\nBooking failed! Passenger name cannot be empty.")
                continue
            
            if not passenger_phone:
                print("\nBooking failed! Phone number cannot be empty.")
                continue
            
            route = system.routes[route_id]
            bus = None
            for b in route.buses:
                if b.bus_id == bus_id:
                    bus = b
                    break
            
            if not bus:
                print("\nBooking failed! Invalid bus ID for this route.")
                continue
            
            if seat_number < 1 or seat_number > bus.total_seats:
                print(f"\nBooking failed! Seat number must be between 1 and {bus.total_seats}.")
                continue
            
            if seat_number in bus.booked_seats:
                print(f"\nBooking failed! Seat {seat_number} is already booked. Please choose another seat.")
                continue
            
            booking = system.create_booking(passenger_name, passenger_phone, 
                                          route_id, bus_id, seat_number)
            
            if booking:
                print("\n" + "="*50)
                print("          BOOKING CONFIRMED!")
                print("="*50)
                print(f"Booking ID: {booking.booking_id}")
                print(f"Passenger: {booking.passenger_name}")
                print(f"Phone: {booking.passenger_phone}")
                print(f"Bus ID: {booking.bus_id}")
                print(f"Seat Number: {booking.seat_number}")
                print(f"Fare: ₹{booking.fare}")
                print(f"Booking Date: {booking.booking_date}")
                print("="*50)
        
        elif choice == "5":
            booking_id = input("Enter booking ID: ").strip()
            if system.cancel_booking(booking_id):
                print(f"\nBooking {booking_id} cancelled successfully!")
            else:
                print("\nCancellation failed! Invalid booking ID.")
        
        elif choice == "6":
            booking_id = input("Enter booking ID: ").strip()
            booking = system.get_booking(booking_id)
            
            if booking:
                print("\n--- Booking Details ---")
                print(f"Booking ID: {booking.booking_id}")
                print(f"Passenger: {booking.passenger_name}")
                print(f"Phone: {booking.passenger_phone}")
                print(f"Route ID: {booking.route_id}")
                print(f"Bus ID: {booking.bus_id}")
                print(f"Seat Number: {booking.seat_number}")
                print(f"Fare: ₹{booking.fare}")
                print(f"Booking Date: {booking.booking_date}")
                print(f"Status: {booking.status}")
            else:
                print("\nBooking not found!")
        
        elif choice == "7":
            print("\n--- Add New Route (Admin) ---")
            route_id = input("Enter route ID: ").strip()
            source = input("Enter source city: ").strip()
            destination = input("Enter destination city: ").strip()
            distance = input("Enter distance (km): ").strip()
            
            if not route_id or not source or not destination:
                print("\nFailed to add route! Route ID, source, and destination cannot be empty.")
                continue
            
            if route_id in system.routes:
                print(f"\nFailed to add route! Route ID {route_id} already exists.")
                continue
            
            try:
                distance = float(distance)
                system.add_route(route_id, source, destination, distance)
                system.save_data()
                print(f"\nRoute {route_id} added successfully!")
            except ValueError:
                print("\nInvalid distance value!")
        
        elif choice == "8":
            print("\n--- Add Bus to Route (Admin) ---")
            route_id = input("Enter route ID: ").strip()
            bus_id = input("Enter bus ID: ").strip()
            bus_name = input("Enter bus name: ").strip()
            total_seats = input("Enter total seats: ").strip()
            fare = input("Enter fare: ").strip()
            
            if not route_id or not bus_id or not bus_name:
                print("\nFailed to add bus! Route ID, bus ID, and bus name cannot be empty.")
                continue
            
            try:
                total_seats = int(total_seats)
                fare = float(fare)
                
                if total_seats <= 0:
                    print("\nFailed to add bus! Total seats must be greater than 0.")
                    continue
                
                if fare <= 0:
                    print("\nFailed to add bus! Fare must be greater than 0.")
                    continue
                
                bus = system.add_bus_to_route(route_id, bus_id, bus_name, total_seats, fare)
                if bus:
                    system.save_data()
                    print(f"\nBus {bus_id} added to route {route_id} successfully!")
                else:
                    print("\nFailed to add bus! Invalid route ID.")
            except ValueError:
                print("\nInvalid input values!")
        
        elif choice == "9":
            print("\nThank you for using Bus Booking System!")
            print("Goodbye!\n")
            break
        
        else:
            print("\nInvalid choice! Please select a valid option (1-9).")


if __name__ == "__main__":
    main()
