import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import deque
import heapq
import random
import string
import json
import os

# ==================== DATA MODELS ====================

# ==================== LINKED LIST FOR PASSENGERS ====================

class PassengerNode:
    """Node for passenger linked list"""
    def __init__(self, seat_number, name="", age=0, gender="Male", is_handicapped=False):
        self.seat_number = seat_number
        self.name = name
        self.age = age
        self.gender = gender
        self.is_handicapped = is_handicapped
        self.next = None
    
    def get_priority(self):
        """Get priority level: 1=Handicapped, 2=Senior, 3=Normal"""
        if self.is_handicapped:
            return 1
        elif self.age > 45:
            return 2
        else:
            return 3
    
    def __str__(self):
        priority = self.get_priority()
        return f"Seat {self.seat_number}: {self.name} (Age: {self.age}, Priority: {priority})"

class PassengerLinkedList:
    """Linked list to store passengers for a booking"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def add_passenger(self, seat_number, name="", age=0, gender="Male", is_handicapped=False):
        """Add passenger at end of list"""
        new_node = PassengerNode(seat_number, name, age, gender, is_handicapped)
        
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        
        self.size += 1
        return new_node
    
    def get_passenger_by_seat(self, seat_number):
        """Find passenger by seat number"""
        current = self.head
        while current:
            if current.seat_number == seat_number:
                return current
            current = current.next
        return None
    
    def get_passenger_at_index(self, index):
        """Get passenger at specific index"""
        if index < 0 or index >= self.size:
            return None
        
        current = self.head
        for _ in range(index):
            current = current.next
        return current
    
    def update_passenger(self, seat_number, name, age, gender, is_handicapped):
        """Update passenger details"""
        passenger = self.get_passenger_by_seat(seat_number)
        if passenger:
            passenger.name = name
            passenger.age = age
            passenger.gender = gender
            passenger.is_handicapped = is_handicapped
            return True
        return False
    
    def remove_passenger(self, seat_number):
        """Remove passenger from list"""
        if self.head is None:
            return False
        
        # If head node is to be removed
        if self.head.seat_number == seat_number:
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self.size -= 1
            return True
        
        # Search for the node
        current = self.head
        while current.next:
            if current.next.seat_number == seat_number:
                if current.next == self.tail:
                    self.tail = current
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        
        return False
    
    def get_all_passengers(self):
        """Return all passengers as list"""
        passengers = []
        current = self.head
        while current:
            passengers.append(current)
            current = current.next
        return passengers
    
    def get_all_seats(self):
        """Return all seat numbers"""
        seats = []
        current = self.head
        while current:
            seats.append(current.seat_number)
            current = current.next
        return seats
    
    def is_empty(self):
        """Check if list is empty"""
        return self.head is None
    
    def clear(self):
        """Clear all passengers"""
        self.head = None
        self.tail = None
        self.size = 0
    
    def __len__(self):
        return self.size
    
    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next
    
    def display(self):
        """Display all passengers"""
        print(f"Passenger List ({self.size} passengers):")
        for passenger in self:
            print(f"  - {passenger}")

class UserSession:
    """Manages user authentication and session"""
    def __init__(self):
        self.current_user = None
        self.is_authenticated = False
        self.users_file = "users.json"
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from file or create default"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {"admin": "admin123", "user": "user123"}  # Default users
    
    def _save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f)
    
    def login(self, username, password):
        """Authenticate user"""
        if username in self.users and self.users[username] == password:
            self.current_user = username
            self.is_authenticated = True
            return True
        return False
    
    def register(self, username, password):
        """Register new user"""
        if username in self.users:
            return False, "Username already exists"
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        self.users[username] = password
        self._save_users()
        return True, "Registration successful"
    
    def logout(self):
        """Clear session"""
        self.current_user = None
        self.is_authenticated = False

class PriorityQueue:
    """Priority queue for waiting passengers"""
    def __init__(self):
        self.heap = []
        self.counter = 0  # For FIFO within same priority
    
    def add_passenger(self, passenger):
        """Add passenger with priority"""
        # Priority levels: 1=Handicapped, 2=Seniors, 3=Normal
        if hasattr(passenger, 'is_handicapped') and passenger.is_handicapped:
            priority = 1
        elif passenger.age > 45:
            priority = 2
        else:
            priority = 3
        
        # Use counter for FIFO within same priority
        heapq.heappush(self.heap, (priority, self.counter, passenger))
        self.counter += 1
    
    def get_next(self):
        """Get highest priority passenger"""
        if self.heap:
            _, _, passenger = heapq.heappop(self.heap)
            return passenger
        return None
    
    def get_position(self, passenger):
        """Get passenger position in queue"""
        for idx, (_, _, p) in enumerate(sorted(self.heap), 1):
            if p.ticket_id == passenger.ticket_id:
                return idx
        return -1
    
    def size(self):
        """Get queue size"""
        return len(self.heap)
    
    def is_empty(self):
        """Check if queue is empty"""
        return len(self.heap) == 0

class Bus:
    """Represents a bus"""
    def __init__(self, bus_id, name, route, departure_time, total_seats, base_price, bus_type):
        self.bus_id = bus_id
        self.name = name
        self.route = route
        self.departure_time = departure_time
        self.total_seats = total_seats
        self.available_seats = total_seats
        self.base_price = base_price
        self.bus_type = bus_type
        self.booked_seats = {}
        self.waiting_queue = PriorityQueue()
        self.seat_layout = self._generate_seat_layout()
    
    def _generate_seat_layout(self):
        """Generate 2-2 seat layout"""
        layout = []
        rows = (self.total_seats + 3) // 4
        seat_num = 1
        
        for row in range(rows):
            row_seats = []
            for col in range(4):
                if seat_num <= self.total_seats:
                    row_seats.append(seat_num)
                    seat_num += 1
                else:
                    row_seats.append(None)
            layout.append(row_seats)
        return layout
    
    def is_seat_booked(self, seat_number):
        """Check if seat is booked"""
        return seat_number in self.booked_seats
    
    def book_seat(self, seat_number, passenger=None):
        """Book specific seat"""
        if not self.is_seat_booked(seat_number):
            self.booked_seats[seat_number] = passenger
            if passenger is not None and hasattr(passenger, 'seat_number'):
                passenger.seat_number = seat_number
            self.available_seats -= 1
            return True
        return False
    
    def cancel_seat(self, seat_number):
        """Cancel a booked seat"""
        if seat_number in self.booked_seats:
            del self.booked_seats[seat_number]
            self.available_seats += 1
            return True
        return False
    
    def get_booked_count(self):
        """Get number of booked seats"""
        return len(self.booked_seats)
    
    def add_to_waiting(self, passenger):
        """Add to priority queue"""
        self.waiting_queue.add_passenger(passenger)
        return self.waiting_queue.get_position(passenger)
    
    def allocate_from_queue(self):
        """Auto-allocate seat from waiting queue"""
        if self.available_seats > 0 and not self.waiting_queue.is_empty():
            passenger = self.waiting_queue.get_next()
            # Find first available seat
            for seat_num in range(1, self.total_seats + 1):
                if not self.is_seat_booked(seat_num):
                    self.book_seat(seat_num, passenger)
                    passenger.status = "Confirmed (Auto-allocated)"
                    return passenger
        return None

class Ticket:
    """Represents a booking ticket"""
    def __init__(self, username, passenger_name, age, gender, bus, seat_number, amount, status, is_handicapped=False, travel_date=None):
        self.ticket_id = self._generate_ticket_id()
        self.username = username
        self.passenger_name = passenger_name
        self.age = age
        self.gender = gender
        self.is_handicapped = is_handicapped
        self.bus_id = bus.bus_id
        self.bus_name = bus.name
        self.route = bus.route
        self.departure_time = bus.departure_time
        self.seat_number = seat_number
        self.amount = amount
        self.status = status
        self.booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.travel_date = travel_date or datetime.now().strftime("%Y-%m-%d")
        self.is_priority = is_handicapped or age > 45
    
    @staticmethod
    def _generate_ticket_id():
        """Generate unique ticket ID"""
        return 'TKT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'ticket_id': self.ticket_id,
            'username': self.username,
            'passenger_name': self.passenger_name,
            'age': self.age,
            'gender': self.gender,
            'is_handicapped': self.is_handicapped,
            'bus_id': self.bus_id,
            'bus_name': self.bus_name,
            'route': self.route,
            'departure_time': self.departure_time,
            'seat_number': self.seat_number,
            'amount': self.amount,
            'status': self.status,
            'booking_time': self.booking_time,
            'travel_date': self.travel_date,
            'is_priority': self.is_priority
        }

# ==================== BOOKING MANAGER ====================

class BookingManager:
    """Manages all bookings and business logic"""
    
    CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
    CONFIRMATION_CHARGE = 50
    
    def __init__(self):
        self.buses = {}
        self.tickets = []
        self.tickets_file = "tickets.json"
        self.buses_file = "buses_data.json"
        self._initialize_buses()
        self._load_tickets()
        self._load_booked_seats()  # Load booked seats from tickets
    
    def _initialize_buses(self):
        """Initialize buses - load from file or create new"""
        if os.path.exists(self.buses_file):
            self._load_buses()
            print("✓ Loaded existing bus database from file")
        else:
            self._create_buses()
            self._save_buses()
            print("✓ Created new bus database and saved to file")
    
    def _create_buses(self):
        """Create buses for all routes (only once)"""
        print("Initializing bus database...")
        bus_names = ["Express Travels", "Swift Transport", "Royal Roadways", "Comfort Coaches"]
        times = ["06:00 AM", "09:00 AM", "12:00 PM", "03:00 PM", "06:00 PM", "09:00 PM"]
        bus_types = ["Seater", "Semi-Sleeper", "Sleeper"]
        
        # Use fixed seed for consistent bus generation
        random.seed(42)
        
        bus_id = 1
        total_buses = 0
        for source in self.CITIES:
            for dest in self.CITIES:
                if source != dest:
                    route_key = f"{source}-{dest}"
                    self.buses[route_key] = []
                    
                    num_buses = random.randint(2, 3)
                    for i in range(num_buses):
                        name = f"{random.choice(bus_names)} #{bus_id}"
                        departure = random.choice(times)
                        seats = random.choice([32, 36, 40])
                        price = random.randint(500, 2000)
                        bus_type = random.choice(bus_types)
                        
                        bus = Bus(bus_id, name, (source, dest), departure, seats, price, bus_type)
                        self.buses[route_key].append(bus)
                        bus_id += 1
                        total_buses += 1
        
        # Reset random seed
        random.seed()
        
        print(f"✓ {total_buses} buses initialized across {len(self.CITIES)} cities")
        print(f"✓ Total routes available: {len([route for route in self.buses.keys()])}")
    
    def _save_buses(self):
        """Save bus data to file"""
        buses_data = {}
        for route_key, bus_list in self.buses.items():
            buses_data[route_key] = []
            for bus in bus_list:
                bus_info = {
                    'bus_id': bus.bus_id,
                    'name': bus.name,
                    'route': bus.route,
                    'departure_time': bus.departure_time,
                    'total_seats': bus.total_seats,
                    'base_price': bus.base_price,
                    'bus_type': bus.bus_type,
                    'booked_seats': list(bus.booked_seats.keys())
                }
                buses_data[route_key].append(bus_info)
        
        with open(self.buses_file, 'w') as f:
            json.dump(buses_data, f, indent=2)
    
    def _load_buses(self):
        """Load bus data from file"""
        with open(self.buses_file, 'r') as f:
            buses_data = json.load(f)
        
        total_buses = 0
        for route_key, bus_list in buses_data.items():
            self.buses[route_key] = []
            for bus_info in bus_list:
                bus = Bus(
                    bus_info['bus_id'],
                    bus_info['name'],
                    tuple(bus_info['route']),
                    bus_info['departure_time'],
                    bus_info['total_seats'],
                    bus_info['base_price'],
                    bus_info['bus_type']
                )
                # Restore booked seats
                for seat_num in bus_info.get('booked_seats', []):
                    bus.booked_seats[seat_num] = True
                
                self.buses[route_key].append(bus)
                total_buses += 1
        
        print(f"✓ {total_buses} buses loaded from database")
        print(f"✓ Total routes available: {len(self.buses)}")
    
    def _load_booked_seats(self):
        """Load booked seats from confirmed tickets"""
        for ticket in self.tickets:
            # Check for any confirmed status (including 'Confirmed (Auto-allocated)')
            status = ticket.get('status', '')
            if 'Confirmed' in status and ticket.get('seat_number'):
                bus_id = ticket['bus_id']
                seat_number = ticket['seat_number']
                
                # Find the bus and mark seat as booked
                for route_buses in self.buses.values():
                    for bus in route_buses:
                        if bus.bus_id == bus_id:
                            if seat_number not in bus.booked_seats:
                                bus.booked_seats[seat_number] = True
                            break
        
        # Save updated bus data
        self._save_buses()
        print("✓ Booked seats synchronized from tickets")
    
    def _load_tickets(self):
        """Load tickets from file"""
        if os.path.exists(self.tickets_file):
            with open(self.tickets_file, 'r') as f:
                tickets_data = json.load(f)
                # Note: We load ticket data but don't recreate full Ticket objects
                # This is for display purposes only
                self.tickets = tickets_data
    
    def _save_tickets(self):
        """Save tickets to file"""
        with open(self.tickets_file, 'w') as f:
            json.dump(self.tickets, f, indent=2)
    
    def get_buses(self, source, destination):
        """Get buses for route"""
        route_key = f"{source}-{destination}"
        return self.buses.get(route_key, [])
    
    def book_ticket(self, ticket):
        """Save ticket booking"""
        self.tickets.append(ticket.to_dict())
        self._save_tickets()
    
    def get_user_tickets(self, username):
        """Get all tickets for user"""
        return [t for t in self.tickets if t['username'] == username]
    
    def check_priority(self, age, is_handicapped=False):
        """Check if passenger has priority"""
        return is_handicapped or age > 45
    
    def cancel_ticket(self, ticket_id):
        """Cancel ticket and free seat"""
        for i, ticket_data in enumerate(self.tickets):
            if ticket_data['ticket_id'] == ticket_id and ticket_data['status'] != 'Cancelled':
                # Update ticket status
                self.tickets[i]['status'] = 'Cancelled'
                
                # Free the seat in the bus
                bus_id = ticket_data['bus_id']
                seat_number = ticket_data.get('seat_number')
                bus_name = ticket_data.get('bus_name', '')
                
                if seat_number:  # Only if seat was allocated
                    # Find the bus and free the seat
                    bus_found = False
                    for route_buses in self.buses.values():
                        for bus in route_buses:
                            if bus.bus_id == bus_id:
                                bus_found = True
                                # Free the seat
                                if seat_number in bus.booked_seats:
                                    del bus.booked_seats[seat_number]
                                    bus.available_seats += 1
                                    print(f"✓ Seat {seat_number} freed from bus {bus.name} (ID: {bus_id})")
                                else:
                                    print(f"⚠ Seat {seat_number} was not in booked_seats for bus {bus_id}")
                                
                                # Find waiting queue ticket for this bus (by bus_id AND bus_name for safety)
                                waiting_ticket_found = False
                                # Sort by priority - find tickets with Waiting Queue status
                                waiting_tickets = [
                                    (idx, t) for idx, t in enumerate(self.tickets)
                                    if t['bus_id'] == bus_id and 
                                       t['status'].startswith('Waiting Queue') and
                                       t.get('seat_number') is None
                                ]
                                
                                # Sort by priority: handicapped first, then seniors
                                def get_priority(ticket_tuple):
                                    t = ticket_tuple[1]
                                    if t.get('is_handicapped'):
                                        return 1
                                    elif t.get('age', 0) > 45:
                                        return 2
                                    else:
                                        return 3
                                
                                waiting_tickets.sort(key=get_priority)
                                
                                if waiting_tickets:
                                    j, waiting_ticket = waiting_tickets[0]
                                    # Update the waiting ticket with pending payment status
                                    self.tickets[j]['seat_number'] = seat_number
                                    self.tickets[j]['status'] = 'Pending Payment (Seat Auto-allocated)'
                                    
                                    # Reserve the seat in the bus (pending confirmation)
                                    bus.booked_seats[seat_number] = 'pending'
                                    bus.available_seats -= 1
                                    
                                    print(f"✓ Seat {seat_number} reserved for {waiting_ticket['passenger_name']} - Pending Payment")
                                    waiting_ticket_found = True
                                
                                if not waiting_ticket_found:
                                    print(f"✓ Seat {seat_number} is now empty (no one in waiting queue for this bus)")
                                break
                        if bus_found:
                            break
                    
                    if not bus_found:
                        print(f"⚠ Bus {bus_id} not found in current session")
                
                self._save_tickets()
                self._save_buses()  # Save bus data after cancellation
                return True, "Ticket cancelled successfully. Refund will be processed."
        
        return False, "Ticket not found or already cancelled"
    
    def confirm_pending_ticket(self, ticket_id):
        """Confirm a pending payment ticket after payment"""
        for i, ticket_data in enumerate(self.tickets):
            if ticket_data['ticket_id'] == ticket_id and 'Pending Payment' in ticket_data.get('status', ''):
                # Update ticket status to Confirmed
                self.tickets[i]['status'] = 'Confirmed (Auto-allocated)'
                
                # Update bus seat from 'pending' to True
                bus_id = ticket_data['bus_id']
                seat_number = ticket_data.get('seat_number')
                
                if seat_number:
                    for route_buses in self.buses.values():
                        for bus in route_buses:
                            if bus.bus_id == bus_id:
                                bus.booked_seats[seat_number] = True
                                print(f"✓ Seat {seat_number} confirmed for {ticket_data['passenger_name']}")
                                break
                
                self._save_tickets()
                self._save_buses()
                return True, "Ticket confirmed successfully."
        
        return False, "Ticket not found or already processed"
    
    def decline_pending_ticket(self, ticket_id):
        """Decline a pending payment ticket and free the seat"""
        for i, ticket_data in enumerate(self.tickets):
            if ticket_data['ticket_id'] == ticket_id and 'Pending Payment' in ticket_data.get('status', ''):
                # Update ticket status to Declined
                self.tickets[i]['status'] = 'Declined (Seat Released)'
                
                # Free the seat
                bus_id = ticket_data['bus_id']
                seat_number = ticket_data.get('seat_number')
                self.tickets[i]['seat_number'] = None  # Remove seat assignment
                
                if seat_number:
                    for route_buses in self.buses.values():
                        for bus in route_buses:
                            if bus.bus_id == bus_id:
                                if seat_number in bus.booked_seats:
                                    del bus.booked_seats[seat_number]
                                    bus.available_seats += 1
                                    print(f"✓ Seat {seat_number} freed after decline by {ticket_data['passenger_name']}")
                                
                                # Try to allocate to next person in waiting queue
                                waiting_tickets = [
                                    (idx, t) for idx, t in enumerate(self.tickets)
                                    if t['bus_id'] == bus_id and 
                                       t['status'].startswith('Waiting Queue') and
                                       t.get('seat_number') is None
                                ]
                                
                                def get_priority(ticket_tuple):
                                    t = ticket_tuple[1]
                                    if t.get('is_handicapped'):
                                        return 1
                                    elif t.get('age', 0) > 45:
                                        return 2
                                    else:
                                        return 3
                                
                                waiting_tickets.sort(key=get_priority)
                                
                                if waiting_tickets:
                                    j, waiting_ticket = waiting_tickets[0]
                                    self.tickets[j]['seat_number'] = seat_number
                                    self.tickets[j]['status'] = 'Pending Payment (Seat Auto-allocated)'
                                    bus.booked_seats[seat_number] = 'pending'
                                    bus.available_seats -= 1
                                    print(f"✓ Seat {seat_number} reserved for next waiting passenger: {waiting_ticket['passenger_name']}")
                                else:
                                    print(f"✓ Seat {seat_number} is now available (no one in waiting queue)")
                                break
                
                self._save_tickets()
                self._save_buses()
                return True, "Seat allocation declined. The seat has been released."
        
        return False, "Ticket not found or already processed"

# ==================== LOGIN PAGE ====================

class LoginPage:
    """Login page UI"""
    
    def __init__(self, root, session, on_login_success):
        self.root = root
        self.session = session
        self.on_login_success = on_login_success
        self.frame = None
        self._create_ui()
    
    def _create_ui(self):
        """Create login UI"""
        # Clear root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.frame = tk.Frame(self.root, bg='#f0f0f0')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Center container
        center_frame = tk.Frame(self.frame, bg='white', relief=tk.RAISED, bd=2)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Header
        header = tk.Frame(center_frame, bg='#007bff', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🚌 Bus Ticket Booking", font=('Arial', 20, 'bold'),
                bg='#007bff', fg='white').pack(expand=True)
        
        # Form
        form_frame = tk.Frame(center_frame, bg='white', padx=50, pady=40)
        form_frame.pack()
        
        tk.Label(form_frame, text="Login to Continue", font=('Arial', 16, 'bold'),
                bg='white', fg='#333').pack(pady=(0, 20))
        
        # Username
        tk.Label(form_frame, text="Username:", font=('Arial', 11),
                bg='white', fg='#555').pack(anchor='w')
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var,
                                   font=('Arial', 11), width=30)
        username_entry.pack(pady=(5, 15), ipady=5)
        username_entry.focus()
        
        # Password
        tk.Label(form_frame, text="Password:", font=('Arial', 11),
                bg='white', fg='#555').pack(anchor='w')
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var,
                                   font=('Arial', 11), width=30, show='*')
        password_entry.pack(pady=(5, 20), ipady=5)
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: self._login())
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(pady=(10, 0))
        
        login_btn = tk.Button(btn_frame, text="Login", font=('Arial', 11, 'bold'),
                             bg='#007bff', fg='white', width=12, height=2,
                             relief=tk.FLAT, cursor='hand2', command=self._login)
        login_btn.pack(side=tk.LEFT, padx=5)
        
        register_btn = tk.Button(btn_frame, text="Register", font=('Arial', 11, 'bold'),
                                bg='#28a745', fg='white', width=12, height=2,
                                relief=tk.FLAT, cursor='hand2', command=self._register)
        register_btn.pack(side=tk.LEFT, padx=5)
        
        # Demo credentials
        demo_frame = tk.Frame(center_frame, bg='#f8f9fa', pady=15)
        demo_frame.pack(fill=tk.X)
        
        tk.Label(demo_frame, text="Demo: admin/admin123 or user/user123",
                font=('Arial', 9, 'italic'), bg='#f8f9fa', fg='#666').pack()
    
    def _login(self):
        """Handle login"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        print(f"\n🔑 Login attempt for user: {username}")
        if self.session.login(username, password):
            print(f"✓ Login successful for user: {username}")
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.frame.destroy()
            self.on_login_success()
        else:
            print(f"✗ Login failed for user: {username}")
            messagebox.showerror("Error", "Invalid username or password")
            self.password_var.set("")
    
    def _register(self):
        """Handle registration"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        success, message = self.session.register(username, password)
        
        if success:
            messagebox.showinfo("Success", message + "\nYou can now login.")
            self.username_var.set("")
            self.password_var.set("")
        else:
            messagebox.showerror("Error", message)

# ==================== SEAT SELECTION WINDOW ====================

class SeatSelectionWindow:
    """Visual seat selection"""
    
    def __init__(self, parent, bus, callback, max_seats=5, travel_date=None, manager=None):
        self.bus = bus
        self.callback = callback
        self.selected_seats = []
        self.max_seats = max_seats
        self.travel_date = travel_date or datetime.now().strftime("%Y-%m-%d")
        self.manager = manager
        
        # Get seats booked for this specific date
        self.date_booked_seats = self._get_date_booked_seats()
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Select Seats (Max {max_seats}) - {bus.name} - {self.travel_date}")
        self.window.geometry("800x700")
        self.window.resizable(True, True)
        self.window.configure(bg='#f0f0f0')
        self.window.grab_set()
        self._center_window()
        self._create_widgets()
    
    def _get_date_booked_seats(self):
        """Get seats booked for this bus on this specific date"""
        booked_seats = set()
        if self.manager:
            for ticket in self.manager.tickets:
                # Get ticket's travel date, falling back to booking date if not set
                ticket_date = ticket.get('travel_date')
                if not ticket_date:
                    booking_time = ticket.get('booking_time', '')
                    if booking_time:
                        ticket_date = booking_time.split(' ')[0]
                
                if (ticket['bus_id'] == self.bus.bus_id and 
                    ticket_date == self.travel_date and
                    ticket.get('seat_number') and
                    'Cancelled' not in ticket.get('status', '') and
                    'Declined' not in ticket.get('status', '')):
                    booked_seats.add(ticket['seat_number'])
        return booked_seats
    
    def _center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create seat selection UI"""
        # Header
        header = tk.Frame(self.window, bg='#007bff', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=f"🚌 {self.bus.name}", font=('Arial', 16, 'bold'),
                bg='#007bff', fg='white').pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(header, text=f"{self.bus.route[0]} → {self.bus.route[1]}", 
                font=('Arial', 12), bg='#007bff', fg='white').pack(side=tk.LEFT, padx=10)
        
        # Info
        info_frame = tk.Frame(self.window, bg='white', padx=20, pady=15)
        info_frame.pack(fill=tk.X)
        
        # Calculate actual available seats for this date
        actual_available = self.bus.total_seats - len(self.date_booked_seats)
        info_text = f"📅 {self.travel_date}  |  ⏰ {self.bus.departure_time}  |  🪑 {self.bus.bus_type}  |  💺 {actual_available}/{self.bus.total_seats} available"
        self.info_label = tk.Label(info_frame, text=info_text, font=('Arial', 10), bg='white')
        self.info_label.pack()
        
        # Legend
        legend_frame = tk.Frame(self.window, bg='#f0f0f0', padx=20, pady=10)
        legend_frame.pack(fill=tk.X)
        
        for text, bg, fg in [("Available", "#28a745", "white"), 
                             ("Selected", "#ffc107", "black"),
                             ("Booked", "#dc3545", "white")]:
            item = tk.Frame(legend_frame, bg='#f0f0f0')
            item.pack(side=tk.LEFT, padx=15)
            tk.Label(item, text="  ", bg=bg, fg=fg, relief=tk.RAISED, bd=2,
                    width=3, height=1).pack(side=tk.LEFT, padx=5)
            tk.Label(item, text=text, font=('Arial', 9), bg='#f0f0f0').pack(side=tk.LEFT)
        
        # Seats
        seat_container = tk.Frame(self.window, bg='white')
        seat_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(seat_container, bg='white')
        scrollbar = ttk.Scrollbar(seat_container, orient='vertical', command=canvas.yview)
        seat_frame = tk.Frame(canvas, bg='white')
        
        seat_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=seat_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Driver
        driver_frame = tk.Frame(seat_frame, bg='white')
        driver_frame.pack(pady=10)
        tk.Label(driver_frame, text="🚗", font=('Arial', 24), bg='white').pack(side=tk.LEFT, padx=10)
        tk.Label(driver_frame, text="DRIVER", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        tk.Frame(seat_frame, bg='#ddd', height=2).pack(fill=tk.X, pady=10, padx=20)
        
        # Seat grid
        self.seat_buttons = {}
        for row_idx, row in enumerate(self.bus.seat_layout):
            row_frame = tk.Frame(seat_frame, bg='white')
            row_frame.pack(pady=5)
            
            for col_idx, seat_num in enumerate(row):
                if seat_num is None:
                    tk.Label(row_frame, text="", width=4, bg='white').pack(side=tk.LEFT, padx=2)
                else:
                    # Check if seat is booked for THIS DATE
                    is_booked = seat_num in self.date_booked_seats
                    bg_color = "#dc3545" if is_booked else "#28a745"
                    fg_color = "white"
                    state = "disabled" if is_booked else "normal"
                    
                    btn = tk.Button(row_frame, text=str(seat_num), font=('Arial', 10, 'bold'),
                                  width=4, height=2, bg=bg_color, fg=fg_color,
                                  activebackground="#ffc107", activeforeground="black",
                                  relief=tk.RAISED, bd=2, state=state,
                                  command=lambda s=seat_num: self.select_seat(s))
                    btn.pack(side=tk.LEFT, padx=3)
                    
                    if not is_booked:
                        self.seat_buttons[seat_num] = btn
                
                if col_idx == 1:
                    tk.Label(row_frame, text="  ", bg='white', width=3).pack(side=tk.LEFT)
        
        # Action buttons
        btn_frame = tk.Frame(self.window, bg='#f0f0f0', pady=15)
        btn_frame.pack(fill=tk.X)
        
        self.confirm_btn = tk.Button(btn_frame, text="✅ Confirm Seat", font=('Arial', 11, 'bold'),
                                     bg='#28a745', fg='white', width=15, height=2,
                                     relief=tk.FLAT, state='disabled', command=self.confirm_selection)
        self.confirm_btn.pack(side=tk.LEFT, padx=(20, 10), expand=True, fill=tk.X)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 11, 'bold'),
                 bg='#dc3545', fg='white', width=15, height=2,
                 relief=tk.FLAT, command=self.window.destroy).pack(side=tk.LEFT, padx=(10, 20), expand=True, fill=tk.X)
        
        # Selected seats display
        self.selected_label = tk.Label(self.window, text="No seats selected (Max 5 seats per booking)", 
                                       font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#666')
        self.selected_label.pack(pady=5)
    
    def select_seat(self, seat_number):
        """Handle seat selection (multiple seats allowed)"""
        if seat_number in self.selected_seats:
            # Deselect seat
            self.selected_seats.remove(seat_number)
            self.seat_buttons[seat_number].config(bg='#28a745', fg='white')
        else:
            # Select seat if under limit
            if len(self.selected_seats) < self.max_seats:
                self.selected_seats.append(seat_number)
                self.seat_buttons[seat_number].config(bg='#ffc107', fg='black')
            else:
                messagebox.showwarning("Limit Reached", f"Maximum {self.max_seats} seats allowed per booking")
                return
        
        # Update available seats info
        actual_available = self.bus.total_seats - len(self.bus.booked_seats)
        remaining = actual_available - len(self.selected_seats)
        info_text = f"⏰ {self.bus.departure_time}  |  🪑 {self.bus.bus_type}  |  💺 {remaining}/{self.bus.total_seats} will remain after booking"
        self.info_label.config(text=info_text)
        
        # Update display
        if self.selected_seats:
            seats_text = ", ".join(map(str, sorted(self.selected_seats)))
            self.selected_label.config(text=f"Selected Seats: {seats_text} ({len(self.selected_seats)}/{self.max_seats})", fg='#007bff')
            self.confirm_btn.config(state='normal')
        else:
            self.selected_label.config(text="No seats selected", fg='#666')
            self.confirm_btn.config(state='disabled')
    
    def confirm_selection(self):
        """Confirm selection"""
        if self.selected_seats:
            self.callback(self.selected_seats)
            self.window.destroy()

# ==================== PASSENGER DETAILS WINDOW ====================

class PassengerDetailsWindow:
    """Window to collect passenger details for all selected seats"""
    
    def __init__(self, parent, bus, selected_seats, callback):
        self.bus = bus
        self.selected_seats = sorted(selected_seats)
        self.callback = callback
        self.current_index = 0
        
        # Initialize linked list for passengers
        self.passenger_list = PassengerLinkedList()
        for seat in self.selected_seats:
            self.passenger_list.add_passenger(seat)
        
        # Variables for current passenger form
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="Male")
        self.handicapped_var = tk.BooleanVar()
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Passenger Details - {bus.name}")
        self.window.geometry("600x550")
        self.window.resizable(True, True)
        self.window.configure(bg='#f0f0f0')
        self.window.grab_set()
        self._center_window()
        self._create_widgets()
    
    def _center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (550 // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create passenger details UI"""
        # Header
        header = tk.Frame(self.window, bg='#007bff', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=f"🚌 {self.bus.name}", font=('Arial', 14, 'bold'),
                bg='#007bff', fg='white').pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(header, text=f"{self.bus.route[0]} → {self.bus.route[1]}", 
                font=('Arial', 11), bg='#007bff', fg='white').pack(side=tk.LEFT, padx=10)
        
        # Progress indicator
        self.progress_frame = tk.Frame(self.window, bg='white', padx=20, pady=15)
        self.progress_frame.pack(fill=tk.X)
        
        self.progress_label = tk.Label(self.progress_frame, 
                                       text=f"Passenger 1 of {len(self.selected_seats)}",
                                       font=('Arial', 14, 'bold'), bg='white', fg='#007bff')
        self.progress_label.pack()
        
        # Seats overview
        seats_text = "Selected Seats: " + ", ".join(map(str, self.selected_seats))
        tk.Label(self.progress_frame, text=seats_text, font=('Arial', 10),
                bg='white', fg='#666').pack(pady=5)
        
        # Current seat indicator
        self.seat_label = tk.Label(self.progress_frame, 
                                   text=f"🪑 Now entering details for Seat {self.selected_seats[0]}",
                                   font=('Arial', 12, 'bold'), bg='white', fg='#28a745')
        self.seat_label.pack(pady=5)
        
        # Passenger form
        form_frame = tk.LabelFrame(self.window, text="Passenger Information", 
                                  font=('Arial', 12, 'bold'), bg='white', padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Name
        tk.Label(form_frame, text="Full Name:", font=('Arial', 11), bg='white').grid(row=0, column=0, sticky='w', pady=10)
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, font=('Arial', 11), width=35)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        name_entry.focus()
        
        # Age
        tk.Label(form_frame, text="Age:", font=('Arial', 11), bg='white').grid(row=1, column=0, sticky='w', pady=10)
        age_entry = ttk.Entry(form_frame, textvariable=self.age_var, font=('Arial', 11), width=10)
        age_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        age_entry.bind('<KeyRelease>', self._update_priority)
        
        # Gender
        tk.Label(form_frame, text="Gender:", font=('Arial', 11), bg='white').grid(row=2, column=0, sticky='w', pady=10)
        gender_frame = tk.Frame(form_frame, bg='white')
        gender_frame.grid(row=2, column=1, sticky='w', padx=10, pady=10)
        
        for gender in ["Male", "Female", "Other"]:
            ttk.Radiobutton(gender_frame, text=gender, variable=self.gender_var, value=gender).pack(side=tk.LEFT, padx=10)
        
        # Handicapped
        tk.Label(form_frame, text="Special Needs:", font=('Arial', 11), bg='white').grid(row=3, column=0, sticky='w', pady=10)
        handicapped_frame = tk.Frame(form_frame, bg='white')
        handicapped_frame.grid(row=3, column=1, sticky='w', padx=10, pady=10)
        
        ttk.Checkbutton(handicapped_frame, text="Handicapped (Priority 1 - Highest)", 
                       variable=self.handicapped_var, command=self._update_priority).pack(side=tk.LEFT)
        
        # Priority display
        self.priority_label = tk.Label(form_frame, text="", font=('Arial', 10, 'bold'),
                                      bg='white', fg='#28a745')
        self.priority_label.grid(row=4, column=0, columnspan=2, pady=15)
        
        # Action buttons
        btn_frame = tk.Frame(self.window, bg='#f0f0f0', pady=15)
        btn_frame.pack(fill=tk.X)
        
        self.prev_btn = tk.Button(btn_frame, text="⬅️ Previous", font=('Arial', 11, 'bold'),
                                  bg='#6c757d', fg='white', width=12, height=2,
                                  relief=tk.FLAT, state='disabled', command=self._previous_passenger)
        self.prev_btn.pack(side=tk.LEFT, padx=(20, 10))
        
        self.next_btn = tk.Button(btn_frame, text="Next ➡️", font=('Arial', 11, 'bold'),
                                  bg='#007bff', fg='white', width=12, height=2,
                                  relief=tk.FLAT, command=self._next_passenger)
        self.next_btn.pack(side=tk.LEFT, padx=10)
        
        self.confirm_btn = tk.Button(btn_frame, text="✅ Confirm All", font=('Arial', 11, 'bold'),
                                     bg='#28a745', fg='white', width=12, height=2,
                                     relief=tk.FLAT, command=self._confirm_all)
        self.confirm_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 11, 'bold'),
                 bg='#dc3545', fg='white', width=12, height=2,
                 relief=tk.FLAT, command=self.window.destroy).pack(side=tk.RIGHT, padx=(10, 20))
        
        # Passenger list display
        list_frame = tk.LabelFrame(self.window, text="Passengers Entered (Linked List)", 
                                  font=('Arial', 10, 'bold'), bg='white', padx=10, pady=10)
        list_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.list_display = tk.Text(list_frame, height=3, font=('Courier', 9), 
                                   state='disabled', wrap=tk.WORD)
        self.list_display.pack(fill=tk.X)
        
        self._update_buttons()
        self._update_list_display()
    
    def _update_priority(self, event=None):
        """Update priority display"""
        is_handicapped = self.handicapped_var.get()
        
        if is_handicapped:
            self.priority_label.config(text="✅ Priority 1 - Handicapped (Highest Priority)", fg='#dc3545')
            return
        
        try:
            age = int(self.age_var.get())
            if age > 45:
                self.priority_label.config(text="✅ Priority 2 - Senior (Above 45 years)", fg='#ff8c00')
            else:
                self.priority_label.config(text="ℹ️ Priority 3 - Normal Passenger", fg='#28a745')
        except ValueError:
            self.priority_label.config(text="")
    
    def _validate_current(self):
        """Validate current passenger details"""
        name = self.name_var.get().strip()
        age_str = self.age_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter passenger name")
            return False
        
        if not age_str:
            messagebox.showerror("Error", "Please enter passenger age")
            return False
        
        try:
            age = int(age_str)
            if age < 1 or age > 120:
                messagebox.showerror("Error", "Invalid age (1-120)")
                return False
        except ValueError:
            messagebox.showerror("Error", "Age must be a number")
            return False
        
        return True
    
    def _save_current(self):
        """Save current passenger details to linked list"""
        seat = self.selected_seats[self.current_index]
        name = self.name_var.get().strip()
        age = int(self.age_var.get())
        gender = self.gender_var.get()
        is_handicapped = self.handicapped_var.get()
        
        self.passenger_list.update_passenger(seat, name, age, gender, is_handicapped)
        self._update_list_display()
    
    def _load_passenger(self, index):
        """Load passenger data for given index"""
        passenger = self.passenger_list.get_passenger_at_index(index)
        if passenger:
            self.name_var.set(passenger.name)
            self.age_var.set(str(passenger.age) if passenger.age > 0 else "")
            self.gender_var.set(passenger.gender)
            self.handicapped_var.set(passenger.is_handicapped)
            self._update_priority()
    
    def _next_passenger(self):
        """Move to next passenger"""
        if not self._validate_current():
            return
        
        self._save_current()
        
        if self.current_index < len(self.selected_seats) - 1:
            self.current_index += 1
            self._load_passenger(self.current_index)
            self._update_ui()
    
    def _previous_passenger(self):
        """Move to previous passenger"""
        self._save_current()
        
        if self.current_index > 0:
            self.current_index -= 1
            self._load_passenger(self.current_index)
            self._update_ui()
    
    def _update_ui(self):
        """Update UI for current passenger"""
        self.progress_label.config(text=f"Passenger {self.current_index + 1} of {len(self.selected_seats)}")
        self.seat_label.config(text=f"🪑 Now entering details for Seat {self.selected_seats[self.current_index]}")
        self._update_buttons()
    
    def _update_buttons(self):
        """Update button states"""
        self.prev_btn.config(state='normal' if self.current_index > 0 else 'disabled')
        
        if self.current_index >= len(self.selected_seats) - 1:
            self.next_btn.config(state='disabled')
        else:
            self.next_btn.config(state='normal')
    
    def _update_list_display(self):
        """Update the linked list display"""
        self.list_display.config(state='normal')
        self.list_display.delete(1.0, tk.END)
        
        display_text = "Linked List: HEAD → "
        passengers = self.passenger_list.get_all_passengers()
        
        for i, p in enumerate(passengers):
            if p.name:
                priority = p.get_priority()
                display_text += f"[Seat {p.seat_number}: {p.name}, P{priority}]"
            else:
                display_text += f"[Seat {p.seat_number}: (empty)]"
            
            if i < len(passengers) - 1:
                display_text += " → "
        
        display_text += " → NULL"
        self.list_display.insert(tk.END, display_text)
        self.list_display.config(state='disabled')
    
    def _confirm_all(self):
        """Confirm all passengers"""
        if not self._validate_current():
            return
        
        self._save_current()
        
        # Check all passengers have been filled
        for passenger in self.passenger_list:
            if not passenger.name:
                messagebox.showerror("Error", f"Please enter details for Seat {passenger.seat_number}")
                return
        
        # Print linked list info to console
        print("\n📋 Passenger Linked List Created:")
        self.passenger_list.display()
        
        # Callback with the linked list
        self.callback(self.passenger_list)
        self.window.destroy()

# ==================== MAIN APPLICATION ====================

class BusBookingApp:
    """Main application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Bus Ticket Booking System")
        self.root.state('zoomed')  # Full screen on Windows
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")
        
        self.session = UserSession()
        self.manager = BookingManager()
        self.selected_bus = None
        self.selected_seats = []
        self.selected_travel_date = datetime.now().strftime("%Y-%m-%d")
        
        # Show login page
        LoginPage(self.root, self.session, self.show_main_app)
    
    def _get_ticket_travel_date(self, ticket):
        """Get ticket's travel date, falling back to booking date if not set"""
        if ticket.get('travel_date'):
            return ticket['travel_date']
        # Fallback: extract date from booking_time
        booking_time = ticket.get('booking_time', '')
        if booking_time:
            return booking_time.split(' ')[0]  # Get date part "2026-01-01"
        return None
    
    def _get_date_booked_seats(self, bus, travel_date):
        """Get seats booked for a specific bus on a specific date"""
        date_booked_seats = set()
        for ticket in self.manager.tickets:
            ticket_date = self._get_ticket_travel_date(ticket)
            if (ticket['bus_id'] == bus.bus_id and 
                ticket_date == travel_date and
                ticket.get('seat_number') and
                'Cancelled' not in ticket.get('status', '') and
                'Declined' not in ticket.get('status', '')):
                date_booked_seats.add(ticket['seat_number'])
        return date_booked_seats
    
    def _is_bus_departed(self, bus, travel_date):
        """Check if bus has already departed for the given date"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # If travel date is in the past, bus has departed
        if travel_date < today:
            return True
        
        # If travel date is today, check time
        if travel_date == today:
            try:
                # Parse departure time (format: "09:00 PM")
                dep_time_str = bus.departure_time
                dep_time = datetime.strptime(dep_time_str, "%I:%M %p")
                dep_datetime = now.replace(hour=dep_time.hour, minute=dep_time.minute, second=0, microsecond=0)
                
                # Bus departed if current time is past departure time
                if now > dep_datetime:
                    return True
            except:
                pass
        
        return False
    
    def show_main_app(self):
        """Show main booking interface"""
        # Clear root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # If admin, show admin panel directly
        if self.session.current_user == 'admin':
            self._show_admin_interface()
            return
        
        # Main container
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_header()
        self._create_booking_ui()
    
    def _show_admin_interface(self):
        """Show admin-only interface"""
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Admin Header
        header = tk.Frame(self.main_frame, bg='#6f42c1', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="⚙️ Admin Dashboard", font=('Arial', 20, 'bold'),
                bg='#6f42c1', fg='white').pack(side=tk.LEFT, padx=20, pady=20)
        
        user_frame = tk.Frame(header, bg='#6f42c1')
        user_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(user_frame, text="👤 Administrator", font=('Arial', 11),
                bg='#6f42c1', fg='white').pack(side=tk.LEFT, padx=10)
        
        tk.Button(user_frame, text="🚪 Logout", font=('Arial', 10, 'bold'),
                 bg='#dc3545', fg='white', relief=tk.FLAT, padx=15, pady=5,
                 cursor='hand2', command=self.logout).pack(side=tk.LEFT, padx=5)
        
        # Admin content area
        content_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create notebook for admin tabs
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: All Tickets
        tickets_frame = tk.Frame(notebook, bg='white')
        notebook.add(tickets_frame, text="📜 All Booked Tickets")
        self._create_admin_tickets_tab(tickets_frame)
        
        # Tab 2: Manage Buses
        buses_frame = tk.Frame(notebook, bg='white')
        notebook.add(buses_frame, text="🚌 Manage Buses")
        self._create_admin_buses_tab(buses_frame)
        
        # Tab 3: Statistics
        stats_frame = tk.Frame(notebook, bg='white')
        notebook.add(stats_frame, text="📊 Statistics")
        self._create_admin_stats_tab(stats_frame)
    
    def _create_admin_tickets_tab(self, parent):
        """Create tab showing all booked tickets for admin interface"""
        # Header with stats
        stats_frame = tk.Frame(parent, bg='#e9ecef', height=60)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        all_tickets = self.manager.tickets
        confirmed = sum(1 for t in all_tickets if 'Confirmed' in t.get('status', ''))
        waiting = sum(1 for t in all_tickets if 'Waiting' in t.get('status', ''))
        cancelled = sum(1 for t in all_tickets if 'Cancelled' in t.get('status', '') or 'Declined' in t.get('status', ''))
        pending = sum(1 for t in all_tickets if 'Pending' in t.get('status', ''))
        
        tk.Label(stats_frame, text=f"📊 Total: {len(all_tickets)} | ✅ Confirmed: {confirmed} | ⏳ Waiting: {waiting} | 🔶 Pending: {pending} | ❌ Cancelled: {cancelled}",
                font=('Arial', 11, 'bold'), bg='#e9ecef').pack(pady=15)
        
        # Tickets list with scrollbar
        container = tk.Frame(parent, bg='white')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for tickets
        columns = ('Ticket ID', 'User', 'Passenger', 'Age', 'Bus', 'Route', 'Seat', 'Amount', 'Status', 'Booked')
        tree = ttk.Treeview(container, columns=columns, show='headings', height=20)
        
        # Configure columns
        tree.heading('Ticket ID', text='Ticket ID')
        tree.heading('User', text='User')
        tree.heading('Passenger', text='Passenger')
        tree.heading('Age', text='Age')
        tree.heading('Bus', text='Bus')
        tree.heading('Route', text='Route')
        tree.heading('Seat', text='Seat')
        tree.heading('Amount', text='Amount')
        tree.heading('Status', text='Status')
        tree.heading('Booked', text='Booked')
        
        tree.column('Ticket ID', width=100)
        tree.column('User', width=80)
        tree.column('Passenger', width=100)
        tree.column('Age', width=40)
        tree.column('Bus', width=130)
        tree.column('Route', width=130)
        tree.column('Seat', width=50)
        tree.column('Amount', width=70)
        tree.column('Status', width=150)
        tree.column('Booked', width=130)
        
        # Scrollbars
        vsb = ttk.Scrollbar(container, orient='vertical', command=tree.yview)
        hsb = ttk.Scrollbar(container, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add tickets to treeview
        for ticket in reversed(all_tickets):
            route = f"{ticket['route'][0]} → {ticket['route'][1]}"
            seat = ticket.get('seat_number', 'N/A') or 'Queue'
            tree.insert('', tk.END, values=(
                ticket['ticket_id'],
                ticket['username'],
                ticket['passenger_name'],
                ticket['age'],
                ticket['bus_name'],
                route,
                seat,
                f"₹{ticket['amount']}",
                ticket['status'],
                ticket['booking_time']
            ))
    
    def _create_admin_buses_tab(self, parent):
        """Create tab for managing buses in admin interface"""
        # Header
        header_frame = tk.Frame(parent, bg='#e9ecef', height=50)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="Select a route to view and manage buses:", 
                font=('Arial', 11, 'bold'), bg='#e9ecef').pack(side=tk.LEFT, padx=10, pady=10)
        
        # Route selection
        route_var = tk.StringVar()
        routes = list(self.manager.buses.keys())
        route_combo = ttk.Combobox(header_frame, textvariable=route_var, values=routes, 
                                   state='readonly', width=30, font=('Arial', 10))
        route_combo.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bus list frame
        bus_container = tk.Frame(parent, bg='white')
        bus_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for buses
        columns = ('Bus ID', 'Bus Name', 'Type', 'Departure', 'Total Seats', 'Booked', 'Available', 'Price', 'Status')
        bus_tree = ttk.Treeview(bus_container, columns=columns, show='headings', height=15)
        
        for col in columns:
            bus_tree.heading(col, text=col)
            bus_tree.column(col, width=100)
        
        bus_tree.column('Bus Name', width=150)
        bus_tree.column('Bus ID', width=60)
        
        vsb = ttk.Scrollbar(bus_container, orient='vertical', command=bus_tree.yview)
        bus_tree.configure(yscrollcommand=vsb.set)
        
        bus_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons frame
        action_frame = tk.Frame(parent, bg='white')
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def load_buses(*args):
            """Load buses for selected route"""
            bus_tree.delete(*bus_tree.get_children())
            route = route_var.get()
            if route and route in self.manager.buses:
                for bus in self.manager.buses[route]:
                    booked = len(bus.booked_seats)
                    available = bus.total_seats - booked
                    status = "Active" if available > 0 else "Full"
                    bus_tree.insert('', tk.END, values=(
                        bus.bus_id,
                        bus.name,
                        bus.bus_type,
                        bus.departure_time,
                        bus.total_seats,
                        booked,
                        available,
                        f"₹{bus.base_price}",
                        status
                    ))
        
        route_combo.bind('<<ComboboxSelected>>', load_buses)
        
        def cancel_selected_bus():
            """Cancel/disable selected bus"""
            selected = bus_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a bus to cancel")
                return
            
            item = bus_tree.item(selected[0])
            bus_id = item['values'][0]
            bus_name = item['values'][1]
            
            result = messagebox.askyesno(
                "Cancel Bus",
                f"Are you sure you want to cancel this bus?\n\n"
                f"Bus: {bus_name}\n"
                f"ID: {bus_id}\n\n"
                f"All passengers will be notified and refunded."
            )
            
            if result:
                route = route_var.get()
                # Cancel all tickets for this bus
                cancelled_count = 0
                for i, ticket in enumerate(self.manager.tickets):
                    if ticket['bus_id'] == bus_id and 'Cancelled' not in ticket.get('status', ''):
                        self.manager.tickets[i]['status'] = 'Cancelled (Bus Cancelled)'
                        cancelled_count += 1
                
                # Remove bus from the route
                if route in self.manager.buses:
                    self.manager.buses[route] = [b for b in self.manager.buses[route] if b.bus_id != bus_id]
                
                self.manager._save_tickets()
                self.manager._save_buses()
                
                messagebox.showinfo("Success", f"Bus {bus_name} cancelled.\n{cancelled_count} ticket(s) have been cancelled.")
                load_buses()
        
        def view_bus_passengers():
            """View passengers for selected bus"""
            selected = bus_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a bus to view passengers")
                return
            
            item = bus_tree.item(selected[0])
            bus_id = item['values'][0]
            bus_name = item['values'][1]
            
            # Create popup window
            pass_win = tk.Toplevel(self.root)
            pass_win.title(f"Passengers - {bus_name}")
            pass_win.geometry("800x500")
            pass_win.configure(bg='white')
            
            tk.Label(pass_win, text=f"🚌 {bus_name} - Passenger List", font=('Arial', 14, 'bold'),
                    bg='white', fg='#007bff').pack(pady=15)
            
            # Get passengers for this bus
            bus_tickets = [t for t in self.manager.tickets if t['bus_id'] == bus_id and 'Cancelled' not in t.get('status', '')]
            
            if not bus_tickets:
                tk.Label(pass_win, text="No passengers booked on this bus", font=('Arial', 12, 'italic'),
                        bg='white', fg='#666').pack(pady=50)
            else:
                # Create treeview
                columns = ('Seat', 'Passenger', 'Age', 'Status', 'Amount', 'Booked By')
                pass_tree = ttk.Treeview(pass_win, columns=columns, show='headings', height=15)
                
                for col in columns:
                    pass_tree.heading(col, text=col)
                    pass_tree.column(col, width=120)
                
                for ticket in sorted(bus_tickets, key=lambda x: x.get('seat_number') or 999):
                    pass_tree.insert('', tk.END, values=(
                        ticket.get('seat_number') or 'Queue',
                        ticket['passenger_name'],
                        ticket['age'],
                        ticket['status'],
                        f"₹{ticket['amount']}",
                        ticket['username']
                    ))
                
                pass_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            tk.Button(pass_win, text="Close", font=('Arial', 10, 'bold'),
                     bg='#6c757d', fg='white', relief=tk.FLAT, padx=20, pady=8,
                     command=pass_win.destroy).pack(pady=10)
        
        def add_new_bus():
            """Open window to add a new bus"""
            add_win = tk.Toplevel(self.root)
            add_win.title("Add New Bus")
            add_win.geometry("500x550")
            add_win.resizable(False, False)
            add_win.configure(bg='white')
            add_win.grab_set()
            
            # Center window
            add_win.update_idletasks()
            x = (add_win.winfo_screenwidth() // 2) - (500 // 2)
            y = (add_win.winfo_screenheight() // 2) - (550 // 2)
            add_win.geometry(f"+{x}+{y}")
            
            tk.Label(add_win, text="➕ Add New Bus", font=('Arial', 16, 'bold'),
                    bg='white', fg='#6f42c1').pack(pady=20)
            
            form_frame = tk.Frame(add_win, bg='white')
            form_frame.pack(fill=tk.BOTH, expand=True, padx=30)
            
            # Bus Name
            tk.Label(form_frame, text="Bus Name:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 2))
            name_var = tk.StringVar()
            tk.Entry(form_frame, textvariable=name_var, font=('Arial', 11), width=40).pack(fill=tk.X)
            
            # Route (Source)
            tk.Label(form_frame, text="Source City:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 2))
            source_var = tk.StringVar()
            source_combo = ttk.Combobox(form_frame, textvariable=source_var, values=BookingManager.CITIES, 
                                        state='readonly', font=('Arial', 11))
            source_combo.pack(fill=tk.X)
            
            # Route (Destination)
            tk.Label(form_frame, text="Destination City:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 2))
            dest_var = tk.StringVar()
            dest_combo = ttk.Combobox(form_frame, textvariable=dest_var, values=BookingManager.CITIES, 
                                      state='readonly', font=('Arial', 11))
            dest_combo.pack(fill=tk.X)
            
            # Departure Time
            tk.Label(form_frame, text="Departure Time:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 2))
            time_var = tk.StringVar()
            times = ["06:00 AM", "08:00 AM", "10:00 AM", "12:00 PM", "02:00 PM", "04:00 PM", "06:00 PM", "08:00 PM", "10:00 PM"]
            time_combo = ttk.Combobox(form_frame, textvariable=time_var, values=times, 
                                      state='readonly', font=('Arial', 11))
            time_combo.pack(fill=tk.X)
            
            # Bus Type
            tk.Label(form_frame, text="Bus Type:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 2))
            type_var = tk.StringVar()
            type_combo = ttk.Combobox(form_frame, textvariable=type_var, 
                                      values=["Seater", "Sleeper", "AC Seater", "AC Sleeper", "Volvo"], 
                                      state='readonly', font=('Arial', 11))
            type_combo.pack(fill=tk.X)
            
            # Total Seats
            tk.Label(form_frame, text="Total Seats:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 2))
            seats_var = tk.StringVar(value="40")
            tk.Entry(form_frame, textvariable=seats_var, font=('Arial', 11), width=40).pack(fill=tk.X)
            
            # Base Price
            tk.Label(form_frame, text="Base Price (₹):", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 2))
            price_var = tk.StringVar(value="500")
            tk.Entry(form_frame, textvariable=price_var, font=('Arial', 11), width=40).pack(fill=tk.X)
            
            def save_bus():
                # Validate inputs
                if not name_var.get().strip():
                    messagebox.showerror("Error", "Please enter bus name")
                    return
                if not source_var.get() or not dest_var.get():
                    messagebox.showerror("Error", "Please select source and destination")
                    return
                if source_var.get() == dest_var.get():
                    messagebox.showerror("Error", "Source and destination cannot be same")
                    return
                if not time_var.get():
                    messagebox.showerror("Error", "Please select departure time")
                    return
                if not type_var.get():
                    messagebox.showerror("Error", "Please select bus type")
                    return
                try:
                    seats = int(seats_var.get())
                    price = int(price_var.get())
                    if seats <= 0 or price <= 0:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid seats and price")
                    return
                
                # Generate new bus ID
                max_id = 0
                for buses in self.manager.buses.values():
                    for bus in buses:
                        if bus.bus_id > max_id:
                            max_id = bus.bus_id
                new_id = max_id + 1
                
                # Create new bus
                route_key = f"{source_var.get()}-{dest_var.get()}"
                new_bus = Bus(
                    new_id,
                    name_var.get().strip(),
                    (source_var.get(), dest_var.get()),
                    time_var.get(),
                    seats,
                    price,
                    type_var.get()
                )
                
                # Add to manager
                if route_key not in self.manager.buses:
                    self.manager.buses[route_key] = []
                self.manager.buses[route_key].append(new_bus)
                
                # Save to file
                self.manager._save_buses()
                
                messagebox.showinfo("Success", f"Bus '{name_var.get()}' added successfully!\nBus ID: {new_id}")
                add_win.destroy()
                
                # Update route combo if needed
                routes = list(self.manager.buses.keys())
                route_combo['values'] = routes
                route_var.set(route_key)
                load_buses()
            
            # Buttons
            btn_frame = tk.Frame(add_win, bg='white')
            btn_frame.pack(pady=20)
            
            tk.Button(btn_frame, text="💾 Save Bus", font=('Arial', 11, 'bold'),
                     bg='#28a745', fg='white', relief=tk.FLAT, padx=25, pady=8,
                     command=save_bus).pack(side=tk.LEFT, padx=10)
            
            tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 11, 'bold'),
                     bg='#6c757d', fg='white', relief=tk.FLAT, padx=25, pady=8,
                     command=add_win.destroy).pack(side=tk.LEFT, padx=10)
        
        def delete_selected_bus():
            """Permanently delete selected bus"""
            selected = bus_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a bus to delete")
                return
            
            item = bus_tree.item(selected[0])
            bus_id = item['values'][0]
            bus_name = item['values'][1]
            booked = item['values'][5]
            
            if booked > 0:
                result = messagebox.askyesno(
                    "Delete Bus",
                    f"⚠️ WARNING: This bus has {booked} booked seat(s)!\n\n"
                    f"Bus: {bus_name}\n"
                    f"ID: {bus_id}\n\n"
                    f"All bookings will be cancelled.\n"
                    f"Are you sure you want to DELETE this bus permanently?"
                )
            else:
                result = messagebox.askyesno(
                    "Delete Bus",
                    f"Are you sure you want to DELETE this bus permanently?\n\n"
                    f"Bus: {bus_name}\n"
                    f"ID: {bus_id}"
                )
            
            if result:
                route = route_var.get()
                # Cancel all tickets for this bus
                cancelled_count = 0
                for i, ticket in enumerate(self.manager.tickets):
                    if ticket['bus_id'] == bus_id and 'Cancelled' not in ticket.get('status', ''):
                        self.manager.tickets[i]['status'] = 'Cancelled (Bus Deleted)'
                        cancelled_count += 1
                
                # Remove bus from the route
                if route in self.manager.buses:
                    self.manager.buses[route] = [b for b in self.manager.buses[route] if b.bus_id != bus_id]
                    # Remove route if no buses left
                    if len(self.manager.buses[route]) == 0:
                        del self.manager.buses[route]
                        routes = list(self.manager.buses.keys())
                        route_combo['values'] = routes
                        route_var.set('')
                
                self.manager._save_tickets()
                self.manager._save_buses()
                
                if cancelled_count > 0:
                    messagebox.showinfo("Success", f"Bus '{bus_name}' deleted permanently.\n{cancelled_count} ticket(s) have been cancelled.")
                else:
                    messagebox.showinfo("Success", f"Bus '{bus_name}' deleted permanently.")
                load_buses()
        
        tk.Button(action_frame, text="👥 View Passengers", font=('Arial', 10, 'bold'),
                 bg='#007bff', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=view_bus_passengers).pack(side=tk.LEFT, padx=10)
        
        tk.Button(action_frame, text="➕ Add Bus", font=('Arial', 10, 'bold'),
                 bg='#6f42c1', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=add_new_bus).pack(side=tk.LEFT, padx=10)
        
        tk.Button(action_frame, text="❌ Cancel Bus", font=('Arial', 10, 'bold'),
                 bg='#dc3545', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=cancel_selected_bus).pack(side=tk.LEFT, padx=10)
        
        tk.Button(action_frame, text="🗑️ Delete Bus", font=('Arial', 10, 'bold'),
                 bg='#343a40', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=delete_selected_bus).pack(side=tk.LEFT, padx=10)
        
        tk.Button(action_frame, text="🔄 Refresh", font=('Arial', 10, 'bold'),
                 bg='#28a745', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=load_buses).pack(side=tk.LEFT, padx=10)
    
    def _create_admin_stats_tab(self, parent):
        """Create statistics tab for admin"""
        # Statistics cards
        cards_frame = tk.Frame(parent, bg='white')
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        all_tickets = self.manager.tickets
        total_buses = sum(len(buses) for buses in self.manager.buses.values())
        total_routes = len(self.manager.buses)
        total_revenue = sum(t['amount'] for t in all_tickets if 'Confirmed' in t.get('status', ''))
        
        # Create stat cards
        stats = [
            ("📜 Total Tickets", len(all_tickets), '#007bff'),
            ("✅ Confirmed", sum(1 for t in all_tickets if 'Confirmed' in t.get('status', '')), '#28a745'),
            ("⏳ Waiting Queue", sum(1 for t in all_tickets if 'Waiting' in t.get('status', '')), '#ffc107'),
            ("🔶 Pending Payment", sum(1 for t in all_tickets if 'Pending' in t.get('status', '')), '#fd7e14'),
            ("❌ Cancelled", sum(1 for t in all_tickets if 'Cancelled' in t.get('status', '') or 'Declined' in t.get('status', '')), '#dc3545'),
            ("🚌 Total Buses", total_buses, '#6f42c1'),
            ("🛣️ Total Routes", total_routes, '#17a2b8'),
            ("💰 Total Revenue", f"₹{total_revenue}", '#28a745'),
        ]
        
        row = 0
        col = 0
        for label, value, color in stats:
            card = tk.Frame(cards_frame, bg=color, width=200, height=120)
            card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
            card.grid_propagate(False)
            
            tk.Label(card, text=label, font=('Arial', 11), bg=color, fg='white').pack(pady=(20, 5))
            tk.Label(card, text=str(value), font=('Arial', 24, 'bold'), bg=color, fg='white').pack()
            
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        # Configure grid
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
    
    def _create_header(self):
        """Create header with logout"""
        header = tk.Frame(self.main_frame, bg='#007bff', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🚌 Bus Ticket Booking System", font=('Arial', 20, 'bold'),
                bg='#007bff', fg='white').pack(side=tk.LEFT, padx=20, pady=20)
        
        user_frame = tk.Frame(header, bg='#007bff')
        user_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(user_frame, text=f"👤 {self.session.current_user}", font=('Arial', 11),
                bg='#007bff', fg='white').pack(side=tk.LEFT, padx=10)
        
        # Admin Panel button (only for admin user)
        if self.session.current_user == 'admin':
            tk.Button(user_frame, text="⚙️ Admin Panel", font=('Arial', 10, 'bold'),
                     bg='#6f42c1', fg='white', relief=tk.FLAT, padx=15, pady=5,
                     cursor='hand2', command=self.show_admin_panel).pack(side=tk.LEFT, padx=5)
        
        tk.Button(user_frame, text="📜 My Bookings", font=('Arial', 10, 'bold'),
                 bg='#ffc107', fg='black', relief=tk.FLAT, padx=15, pady=5,
                 cursor='hand2', command=self.show_bookings).pack(side=tk.LEFT, padx=5)
        
        tk.Button(user_frame, text="🚪 Logout", font=('Arial', 10, 'bold'),
                 bg='#dc3545', fg='white', relief=tk.FLAT, padx=15, pady=5,
                 cursor='hand2', command=self.logout).pack(side=tk.LEFT, padx=5)
    
    def _create_booking_ui(self):
        """Create booking interface"""
        container = tk.Frame(self.main_frame, bg='#f0f0f0')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Journey details
        journey_frame = tk.LabelFrame(container, text="Journey Details", font=('Arial', 12, 'bold'),
                                     bg='white', padx=20, pady=15)
        journey_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(journey_frame, text="From:", font=('Arial', 10), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.source_var = tk.StringVar()
        ttk.Combobox(journey_frame, textvariable=self.source_var, values=BookingManager.CITIES,
                    state='readonly', width=20).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(journey_frame, text="To:", font=('Arial', 10), bg='white').grid(row=0, column=2, sticky='w', padx=(20,0), pady=5)
        self.dest_var = tk.StringVar()
        ttk.Combobox(journey_frame, textvariable=self.dest_var, values=BookingManager.CITIES,
                    state='readonly', width=20).grid(row=0, column=3, padx=10, pady=5)
        
        tk.Label(journey_frame, text="Date:", font=('Arial', 10), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(journey_frame, textvariable=self.date_var, width=22).grid(row=1, column=1, padx=10, pady=5)
        
        tk.Button(journey_frame, text="🔍 Search Buses", font=('Arial', 10, 'bold'),
                 bg='#007bff', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=self.search_buses).grid(row=1, column=2, columnspan=2, padx=10, pady=5, sticky='ew')
        
        # Bus list
        bus_frame = tk.LabelFrame(container, text="Available Buses", font=('Arial', 12, 'bold'),
                                 bg='white', padx=20, pady=15)
        bus_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        canvas = tk.Canvas(bus_frame, bg='white', height=180)
        scrollbar = ttk.Scrollbar(bus_frame, orient='vertical', command=canvas.yview)
        self.bus_list_frame = tk.Frame(canvas, bg='white')
        
        self.bus_list_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.bus_list_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(self.bus_list_frame, text="Select route and search for buses",
                font=('Arial', 10, 'italic'), bg='white', fg='#999').pack(pady=40)
        
        # Instructions panel
        info_frame = tk.LabelFrame(container, text="📌 How to Book & Priority System", font=('Arial', 12, 'bold'),
                                  bg='white', padx=20, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        left_info = tk.Frame(info_frame, bg='white')
        left_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        booking_steps = """Booking Steps:
1. Select source and destination, click "Search Buses"
2. Click "Select Seats" on your preferred bus
3. Choose up to 5 seats
4. Enter details for EACH passenger (in next window)
5. Confirm and pay"""
        tk.Label(left_info, text=booking_steps, font=('Arial', 9), bg='white',
                justify=tk.LEFT, anchor='w').pack(anchor='w')
        
        right_info = tk.Frame(info_frame, bg='white')
        right_info.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        priority_info = """🏥 Priority System (for waiting queue):
  • Priority 1: Handicapped passengers (Highest)
  • Priority 2: Senior passengers (Age > 45)
  • Priority 3: Normal passengers

💡 Passengers stored in Linked List data structure"""
        tk.Label(right_info, text=priority_info, font=('Arial', 9), bg='white',
                justify=tk.LEFT, anchor='w').pack(anchor='w')
        
        # Initialize variables for waiting queue (used when bus is full)
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="Male")
        self.handicapped_var = tk.BooleanVar()
        
        # Action buttons
        btn_frame = tk.Frame(container, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X)
        
        self.book_btn = tk.Button(btn_frame, text="📋 Book Ticket", font=('Arial', 11, 'bold'),
                                  bg='#28a745', fg='white', relief=tk.FLAT, height=2,
                                  state='disabled', command=self.initiate_booking)
        self.book_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        tk.Button(btn_frame, text="🔄 Reset", font=('Arial', 11, 'bold'),
                 bg='#007bff', fg='white', relief=tk.FLAT, height=2,
                 command=self.reset_form).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    def search_buses(self):
        """Search buses"""
        source = self.source_var.get()
        dest = self.dest_var.get()
        
        if not source or not dest:
            messagebox.showerror("Error", "Please select source and destination")
            return
        
        if source == dest:
            messagebox.showerror("Error", "Source and destination cannot be same")
            return
        
        for widget in self.bus_list_frame.winfo_children():
            widget.destroy()
        
        buses = self.manager.get_buses(source, dest)
        travel_date = self.date_var.get()
        
        # Filter out departed buses
        available_buses = [bus for bus in buses if not self._is_bus_departed(bus, travel_date)]
        
        if not available_buses:
            if buses:
                tk.Label(self.bus_list_frame, text="All buses have departed for this date. Please select a future date.",
                        font=('Arial', 10, 'italic'), bg='white', fg='#dc3545').pack(pady=40)
            else:
                tk.Label(self.bus_list_frame, text="No buses available",
                        font=('Arial', 10, 'italic'), bg='white', fg='#dc3545').pack(pady=40)
            return
        
        for bus in available_buses:
            self._create_bus_card(bus)
    
    def _create_bus_card(self, bus):
        """Create bus card"""
        card = tk.Frame(self.bus_list_frame, bg='#f8f9fa', relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, padx=5, pady=5)
        
        info_frame = tk.Frame(card, bg='#f8f9fa')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tk.Label(info_frame, text=bus.name, font=('Arial', 11, 'bold'),
                bg='#f8f9fa', fg='#333').pack(anchor='w')
        
        # Calculate actual available seats for this specific date using helper
        travel_date = self.date_var.get()
        date_booked_seats = self._get_date_booked_seats(bus, travel_date)
        
        actual_available = bus.total_seats - len(date_booked_seats)
        details = f"🕐 {bus.departure_time}  |  🪑 {bus.bus_type}  |  💺 {actual_available}/{bus.total_seats} seats  |  💰 ₹{bus.base_price}"
        tk.Label(info_frame, text=details, font=('Arial', 9),
                bg='#f8f9fa', fg='#666').pack(anchor='w', pady=(5, 0))
        
        if actual_available > 0:
            btn_text = "Select Seats →"
            btn_bg = '#007bff'
        else:
            btn_text = "Join Waiting Queue"
            btn_bg = '#ffc107'
        
        tk.Button(card, text=btn_text, font=('Arial', 10, 'bold'),
                 bg=btn_bg, fg='white' if actual_available > 0 else 'black',
                 relief=tk.FLAT, padx=20, pady=8,
                 command=lambda b=bus: self.select_bus(b)).pack(side=tk.RIGHT, padx=15, pady=10)
    
    def select_bus(self, bus):
        """Select bus"""
        self.selected_bus = bus
        
        # Get travel date from form and store as instance variable
        travel_date = self.date_var.get()
        self.selected_travel_date = travel_date
        
        # Calculate available seats for this specific date using helper
        date_booked_seats = self._get_date_booked_seats(bus, travel_date)
        actual_available = bus.total_seats - len(date_booked_seats)
        
        # Check if seats available
        if actual_available == 0:
            response = messagebox.askyesno("Bus Full",
                f"No seats available for {travel_date}.\n\n" +
                "Passenger will be added to the waiting queue based on priority.\n\n" +
                "Priority Order:\n" +
                "1. Handicapped passengers\n" +
                "2. Senior passengers (above 45)\n" +
                "3. Normal passengers\n\n" +
                "Do you want to join the waiting queue?")
            
            if response:
                self.add_to_waiting_queue()
            return
        
        # Open seat selection with travel date - no passenger details needed yet
        SeatSelectionWindow(self.root, bus, self.on_seat_selected, max_seats=5, 
                           travel_date=travel_date, manager=self.manager)
    
    def on_seat_selected(self, seat_numbers):
        """Seat selected callback - now open passenger details window"""
        self.selected_seats = seat_numbers
        
        # Open passenger details window for each seat
        PassengerDetailsWindow(self.root, self.selected_bus, seat_numbers, self.on_passengers_confirmed)
    
    def on_passengers_confirmed(self, passenger_list):
        """Callback when all passenger details are confirmed"""
        self.passenger_linked_list = passenger_list
        self.selected_seats = passenger_list.get_all_seats()
        self.book_btn.config(state='normal')
        
        seats_text = ", ".join(map(str, sorted(self.selected_seats)))
        messagebox.showinfo("Ready to Book", 
                           f"All {len(self.selected_seats)} passenger(s) details confirmed for seats: {seats_text}\n\n"
                           "Click 'Book Ticket' to proceed with payment.")
    
    def add_to_waiting_queue(self):
        """Add to waiting queue - show form for passenger details"""
        bus = self.selected_bus
        
        # Create a simple window to get passenger details for waiting queue
        wait_win = tk.Toplevel(self.root)
        wait_win.title("Join Waiting Queue")
        wait_win.geometry("450x400")
        wait_win.resizable(False, False)
        wait_win.configure(bg='white')
        wait_win.grab_set()
        
        # Center window
        wait_win.update_idletasks()
        x = (wait_win.winfo_screenwidth() // 2) - (450 // 2)
        y = (wait_win.winfo_screenheight() // 2) - (400 // 2)
        wait_win.geometry(f"+{x}+{y}")
        
        tk.Label(wait_win, text="⏳ Join Waiting Queue", font=('Arial', 16, 'bold'),
                bg='white', fg='#007bff').pack(pady=20)
        
        tk.Label(wait_win, text=f"Bus: {bus.name}\nRoute: {bus.route[0]} → {bus.route[1]}",
                font=('Arial', 10), bg='white', fg='#666').pack()
        
        form_frame = tk.Frame(wait_win, bg='white', padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(form_frame, text="Name:", font=('Arial', 11), bg='white').grid(row=0, column=0, sticky='w', pady=10)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, pady=10)
        
        tk.Label(form_frame, text="Age:", font=('Arial', 11), bg='white').grid(row=1, column=0, sticky='w', pady=10)
        age_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=age_var, width=10).grid(row=1, column=1, sticky='w', pady=10)
        
        tk.Label(form_frame, text="Gender:", font=('Arial', 11), bg='white').grid(row=2, column=0, sticky='w', pady=10)
        gender_var = tk.StringVar(value="Male")
        gender_frame = tk.Frame(form_frame, bg='white')
        gender_frame.grid(row=2, column=1, sticky='w', pady=10)
        for g in ["Male", "Female", "Other"]:
            ttk.Radiobutton(gender_frame, text=g, variable=gender_var, value=g).pack(side=tk.LEFT, padx=5)
        
        tk.Label(form_frame, text="Handicapped:", font=('Arial', 11), bg='white').grid(row=3, column=0, sticky='w', pady=10)
        handicapped_var = tk.BooleanVar()
        ttk.Checkbutton(form_frame, text="Yes (Priority 1)", variable=handicapped_var).grid(row=3, column=1, sticky='w', pady=10)
        
        def submit_waiting():
            name = name_var.get().strip()
            age_str = age_var.get().strip()
            
            if not name or not age_str:
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            try:
                age = int(age_str)
            except ValueError:
                messagebox.showerror("Error", "Age must be a number")
                return
            
            gender = gender_var.get()
            is_handicapped = handicapped_var.get()
            
            # Create temporary passenger object for queue
            class TempPassenger:
                def __init__(self, name, age, is_handicapped=False):
                    self.name = name
                    self.age = age
                    self.is_handicapped = is_handicapped
                    self.ticket_id = 'TEMP' + ''.join(random.choices(string.digits, k=6))
            
            temp_passenger = TempPassenger(name, age, is_handicapped)
            position = bus.add_to_waiting(temp_passenger)
            
            # Create ticket with waiting status
            ticket = Ticket(self.session.current_user, name, age, gender, bus, 
                           None, bus.base_price + BookingManager.CONFIRMATION_CHARGE,
                           f"Waiting Queue (Position #{position})", is_handicapped,
                           travel_date=self.selected_travel_date)
            
            self.manager.book_ticket(ticket)
            
            if is_handicapped:
                priority_type = "Highest Priority (Handicapped)"
            elif age > 45:
                priority_type = "High Priority (Senior)"
            else:
                priority_type = "Normal Priority"
            
            wait_win.destroy()
            
            messagebox.showinfo("Added to Queue",
                f"✅ Added to Waiting Queue\n\n" +
                f"Position: #{position}\n" +
                f"Priority: {priority_type}\n" +
                f"Ticket ID: {ticket.ticket_id}\n\n" +
                f"You will be notified when a seat becomes available.\n" +
                f"Seat will be auto-allocated based on priority.")
            
            self.reset_form()
            self.search_buses()
        
        btn_frame = tk.Frame(wait_win, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="✅ Join Queue", font=('Arial', 11, 'bold'),
                 bg='#28a745', fg='white', width=12, height=2,
                 relief=tk.FLAT, command=submit_waiting).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 11, 'bold'),
                 bg='#dc3545', fg='white', width=12, height=2,
                 relief=tk.FLAT, command=wait_win.destroy).pack(side=tk.LEFT, padx=10)
    
    def initiate_booking(self):
        """Initiate booking"""
        if not self.selected_seats or not hasattr(self, 'passenger_linked_list'):
            messagebox.showerror("Error", "Please select seats and enter passenger details first")
            return
        
        self.show_confirmation()
    
    def show_confirmation(self):
        """Show confirmation dialog"""
        bus = self.selected_bus
        passengers = self.passenger_linked_list.get_all_passengers()
        
        seats_count = len(passengers)
        base_price = bus.base_price * seats_count
        conf_charge = BookingManager.CONFIRMATION_CHARGE * seats_count
        total = base_price + conf_charge
        
        seats_text = ", ".join(map(str, sorted(self.selected_seats)))
        
        # Build passenger details string from linked list
        passenger_details = ""
        for i, p in enumerate(passengers, 1):
            priority = p.get_priority()
            priority_text = {1: "Handicapped", 2: "Senior", 3: "Normal"}.get(priority, "Normal")
            handicapped_text = " (Handicapped)" if p.is_handicapped else ""
            passenger_details += f"\n  {i}. Seat {p.seat_number}: {p.name}, Age: {p.age}, {p.gender}{handicapped_text}"
            passenger_details += f"\n     → Priority {priority} ({priority_text})"
        
        message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BOOKING CONFIRMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Route: {bus.route[0]} → {bus.route[1]}
Bus: {bus.name} ({bus.bus_type})
Departure: {bus.departure_time}
Date: {self.date_var.get()}
Seats: {seats_text} ({seats_count} seats)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASSENGERS (Linked List):
{passenger_details}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Base Price (₹{bus.base_price} x {seats_count}):  ₹{base_price}
Confirmation Charge (₹{BookingManager.CONFIRMATION_CHARGE} x {seats_count}): ₹{conf_charge}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL AMOUNT:         ₹{total}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proceed with booking for {seats_count} passenger(s)?
        """
        
        if messagebox.askyesno("Confirm Booking", message):
            self.process_payment(total)
        else:
            messagebox.showinfo("Cancelled", "Booking cancelled")
    
    def process_payment(self, amount):
        """Payment simulation"""
        payment_win = tk.Toplevel(self.root)
        payment_win.title("Payment Gateway")
        payment_win.geometry("450x300")
        payment_win.resizable(False, False)
        payment_win.configure(bg='white')
        payment_win.grab_set()
        
        # Center window
        payment_win.update_idletasks()
        x = (payment_win.winfo_screenwidth() // 2) - (450 // 2)
        y = (payment_win.winfo_screenheight() // 2) - (300 // 2)
        payment_win.geometry(f"+{x}+{y}")
        
        tk.Label(payment_win, text="💳 Payment Gateway", font=('Arial', 18, 'bold'),
                bg='white', fg='#007bff').pack(pady=30)
        
        tk.Label(payment_win, text=f"Amount to Pay: ₹{amount}", font=('Arial', 16, 'bold'),
                bg='white').pack(pady=15)
        
        tk.Label(payment_win, text="(Simulated Payment)", font=('Arial', 10, 'italic'),
                bg='white', fg='#666').pack()
        
        def complete_payment():
            payment_win.destroy()
            self.complete_booking(amount)
        
        def cancel_payment():
            payment_win.destroy()
            messagebox.showwarning("Cancelled", "Payment cancelled")
        
        btn_frame = tk.Frame(payment_win, bg='white')
        btn_frame.pack(pady=40)
        
        tk.Button(btn_frame, text="💰 Pay Now", font=('Arial', 12, 'bold'),
                 bg='#28a745', fg='white', width=12, height=2,
                 relief=tk.FLAT, command=complete_payment).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 12, 'bold'),
                 bg='#dc3545', fg='white', width=12, height=2,
                 relief=tk.FLAT, command=cancel_payment).pack(side=tk.LEFT, padx=10)
    
    def complete_booking(self, amount):
        """Complete booking using passenger linked list"""
        bus = self.selected_bus
        passengers = self.passenger_linked_list.get_all_passengers()
        
        tickets = []
        per_seat_amount = amount // len(passengers)
        
        print("\n🎫 Processing booking from Linked List:")
        
        # Book all selected seats using linked list data
        current = self.passenger_linked_list.head
        while current:
            bus.book_seat(current.seat_number, None)
            
            # Create ticket for each passenger from linked list
            ticket = Ticket(
                self.session.current_user, 
                current.name, 
                current.age, 
                current.gender, 
                bus,
                current.seat_number, 
                per_seat_amount, 
                "Confirmed", 
                current.is_handicapped,
                travel_date=self.selected_travel_date
            )
            
            self.manager.book_ticket(ticket)
            tickets.append(ticket)
            
            print(f"  ✓ Booked: Seat {current.seat_number} - {current.name} (Priority {current.get_priority()})")
            
            current = current.next
        
        # Check if anyone in waiting queue
        for _ in passengers:
            allocated = bus.allocate_from_queue()
            if allocated:
                # Create ticket for auto-allocated passenger
                auto_ticket = Ticket(self.session.current_user, allocated.name, allocated.age,
                                   "N/A", bus, allocated.seat_number,
                                   bus.base_price + BookingManager.CONFIRMATION_CHARGE,
                                   "Confirmed (Auto-allocated)",
                                   travel_date=self.selected_travel_date)
                self.manager.book_ticket(auto_ticket)
        
        print(f"✅ Total {len(tickets)} tickets booked successfully!\n")
        
        # Save bus data to persist booked seats
        self.manager._save_buses()
        
        messagebox.showinfo("Payment Success", f"✅ Payment successful!\n\n{len(tickets)} ticket(s) booked.")
        self.show_multiple_tickets(tickets)
        
        self.reset_form()
        self.search_buses()
    
    def show_ticket(self, ticket):
        """Display ticket"""
        ticket_win = tk.Toplevel(self.root)
        ticket_win.title("Ticket Confirmation")
        ticket_win.geometry("550x650")
        ticket_win.resizable(False, False)
        ticket_win.configure(bg='white')
        
        # Center window
        ticket_win.update_idletasks()
        x = (ticket_win.winfo_screenwidth() // 2) - (550 // 2)
        y = (ticket_win.winfo_screenheight() // 2) - (650 // 2)
        ticket_win.geometry(f"+{x}+{y}")
        
        ticket_frame = tk.Frame(ticket_win, bg='white', padx=30, pady=20)
        ticket_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(ticket_frame, text="🎫 TICKET CONFIRMED", font=('Arial', 20, 'bold'),
                bg='white', fg='#28a745').pack(pady=15)
        
        tk.Frame(ticket_frame, bg='#ddd', height=2).pack(fill=tk.X, pady=10)
        
        ticket_text = f"""
Ticket ID: {ticket.ticket_id}
Status: {ticket.status}
Booking Time: {ticket.booking_time}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASSENGER DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {ticket.passenger_name}
Age: {ticket.age} years
Gender: {ticket.gender}
{"Priority: YES ✅" if ticket.is_priority else "Priority: NO"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JOURNEY DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Route: {ticket.route[0]} → {ticket.route[1]}
Bus: {ticket.bus_name}
Departure: {ticket.departure_time}
Date: {self.date_var.get()}
{"Seat Number: " + str(ticket.seat_number) if ticket.seat_number else "Waiting Queue"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAYMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Paid: ₹{ticket.amount}
Payment Status: SUCCESS ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Booked by: {ticket.username}
        """
        
        tk.Label(ticket_frame, text=ticket_text, font=('Courier', 10),
                bg='white', justify=tk.LEFT).pack(pady=10)
        
        btn_frame = tk.Frame(ticket_frame, bg='white')
        btn_frame.pack(pady=20)
        
        def save_ticket():
            filename = f"ticket_{ticket.ticket_id}.txt"
            with open(filename, 'w') as f:
                f.write(ticket_text)
            messagebox.showinfo("Saved", f"Ticket saved as {filename}")
        
        tk.Button(btn_frame, text="💾 Save Ticket", font=('Arial', 11, 'bold'),
                 bg='#007bff', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=save_ticket).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✅ Close", font=('Arial', 11, 'bold'),
                 bg='#28a745', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=ticket_win.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_multiple_tickets(self, tickets):
        """Display multiple tickets"""
        ticket_win = tk.Toplevel(self.root)
        ticket_win.title("Booking Confirmation")
        ticket_win.geometry("600x700")
        ticket_win.resizable(False, False)
        ticket_win.configure(bg='white')
        
        # Center window
        ticket_win.update_idletasks()
        x = (ticket_win.winfo_screenwidth() // 2) - (600 // 2)
        y = (ticket_win.winfo_screenheight() // 2) - (700 // 2)
        ticket_win.geometry(f"+{x}+{y}")
        
        # Scrollable frame
        canvas = tk.Canvas(ticket_win, bg='white')
        scrollbar = ttk.Scrollbar(ticket_win, orient='vertical', command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg='white')
        
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        tk.Label(scroll_frame, text="🎫 BOOKING CONFIRMED", font=('Arial', 20, 'bold'),
                bg='white', fg='#28a745').pack(pady=15)
        
        tk.Label(scroll_frame, text=f"Total Seats Booked: {len(tickets)}", font=('Arial', 14, 'bold'),
                bg='white', fg='#007bff').pack(pady=5)
        
        for i, ticket in enumerate(tickets, 1):
            # Ticket frame
            ticket_frame = tk.Frame(scroll_frame, bg='#f8f9fa', relief=tk.RAISED, bd=1)
            ticket_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(ticket_frame, text=f"SEAT {i}: {ticket.seat_number}", font=('Arial', 12, 'bold'),
                    bg='#007bff', fg='white', padx=10, pady=5).pack(fill=tk.X)
            
            handicapped_text = " (Handicapped)" if ticket.is_handicapped else ""
            ticket_text = f"""Ticket ID: {ticket.ticket_id}
Passenger: {ticket.passenger_name}{handicapped_text}
Amount: ₹{ticket.amount}
Status: {ticket.status}"""
            
            tk.Label(ticket_frame, text=ticket_text, font=('Courier', 9),
                    bg='#f8f9fa', justify=tk.LEFT, padx=10, pady=10).pack(anchor='w')
        
        # Action buttons
        btn_frame = tk.Frame(scroll_frame, bg='white')
        btn_frame.pack(pady=20)
        
        def save_all_tickets():
            for i, ticket in enumerate(tickets, 1):
                filename = f"ticket_{ticket.ticket_id}_seat{ticket.seat_number}.txt"
                ticket_text = f"Ticket ID: {ticket.ticket_id}\nSeat: {ticket.seat_number}\nAmount: ₹{ticket.amount}"
                with open(filename, 'w') as f:
                    f.write(ticket_text)
            messagebox.showinfo("Saved", f"All {len(tickets)} tickets saved!")
        
        tk.Button(btn_frame, text="💾 Save All", font=('Arial', 11, 'bold'),
                 bg='#007bff', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=save_all_tickets).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✅ Close", font=('Arial', 11, 'bold'),
                 bg='#28a745', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=ticket_win.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_bookings(self):
        """Show booking history"""
        bookings_win = tk.Toplevel(self.root)
        bookings_win.title("My Bookings")
        bookings_win.geometry("900x600")
        bookings_win.configure(bg='#f0f0f0')
        
        # Center window
        bookings_win.update_idletasks()
        x = (bookings_win.winfo_screenwidth() // 2) - (900 // 2)
        y = (bookings_win.winfo_screenheight() // 2) - (600 // 2)
        bookings_win.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(bookings_win, bg='#007bff', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📜 My Booking History", font=('Arial', 18, 'bold'),
                bg='#007bff', fg='white').pack(pady=15)
        
        # Get user tickets
        user_tickets = self.manager.get_user_tickets(self.session.current_user)
        
        if not user_tickets:
            tk.Label(bookings_win, text="No bookings found", font=('Arial', 14, 'italic'),
                    bg='#f0f0f0', fg='#666').pack(pady=100)
            return
        
        # Scrollable frame
        container = tk.Frame(bookings_win, bg='white')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(container, bg='white')
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg='white')
        
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display tickets
        for idx, ticket_data in enumerate(reversed(user_tickets), 1):
            self._create_ticket_card(scroll_frame, ticket_data, idx)
    
    def _create_ticket_card(self, parent, ticket_data, index):
        """Create ticket card in history"""
        card = tk.Frame(parent, bg='#f8f9fa', relief=tk.RAISED, bd=2)
        card.pack(fill=tk.X, padx=10, pady=10)
        
        # Header
        header = tk.Frame(card, bg='#007bff')
        header.pack(fill=tk.X)
        
        tk.Label(header, text=f"Ticket #{index}", font=('Arial', 11, 'bold'),
                bg='#007bff', fg='white').pack(side=tk.LEFT, padx=15, pady=8)
        
        # Status color: green for confirmed, red for cancelled, orange for pending, yellow for waiting
        if 'Cancelled' in ticket_data['status'] or 'Declined' in ticket_data['status']:
            status_color = '#dc3545'  # Red for cancelled/declined
            status_fg = 'white'
        elif 'Pending Payment' in ticket_data['status']:
            status_color = '#fd7e14'  # Orange for pending payment
            status_fg = 'white'
        elif 'Confirmed' in ticket_data['status']:
            status_color = '#28a745'  # Green for confirmed
            status_fg = 'white'
        else:
            status_color = '#ffc107'  # Yellow for waiting
            status_fg = 'black'
        
        tk.Label(header, text=ticket_data['status'], font=('Arial', 10, 'bold'),
                bg=status_color, fg=status_fg,
                padx=10, pady=5).pack(side=tk.RIGHT, padx=15)
        
        # Content
        content = tk.Frame(card, bg='#f8f9fa', padx=20, pady=15)
        content.pack(fill=tk.BOTH)
        
        info_text = f"""
🎫 Ticket ID: {ticket_data['ticket_id']}
👤 Passenger: {ticket_data['passenger_name']} ({ticket_data['age']} years)
🚌 Route: {ticket_data['route'][0]} → {ticket_data['route'][1]}
🚍 Bus: {ticket_data['bus_name']}
🕐 Departure: {ticket_data['departure_time']}
{"💺 Seat: " + str(ticket_data['seat_number']) if ticket_data['seat_number'] else "⏳ Waiting Queue"}
💰 Amount: ₹{ticket_data['amount']}
📅 Booked: {ticket_data['booking_time']}
{"✅ Priority Passenger" if ticket_data['is_priority'] else ""}
        """
        
        tk.Label(content, text=info_text, font=('Arial', 10),
                bg='#f8f9fa', justify=tk.LEFT, anchor='w').pack(anchor='w')
        
        # Action buttons
        action_frame = tk.Frame(content, bg='#f8f9fa')
        action_frame.pack(anchor='e', pady=(10, 0))
        
        tk.Button(action_frame, text="📄 View Details", font=('Arial', 9, 'bold'),
                 bg='#007bff', fg='white', relief=tk.FLAT, padx=15, pady=5,
                 command=lambda t=ticket_data: self._show_ticket_details(t)).pack(side=tk.LEFT, padx=2)
        
        # Show Pay Now and Decline buttons for pending payment tickets
        if 'Pending Payment' in ticket_data['status']:
            tk.Button(action_frame, text="💰 Pay Now", font=('Arial', 9, 'bold'),
                     bg='#28a745', fg='white', relief=tk.FLAT, padx=15, pady=5,
                     command=lambda t=ticket_data: self._confirm_pending_payment(t)).pack(side=tk.LEFT, padx=2)
            tk.Button(action_frame, text="❌ Decline", font=('Arial', 9, 'bold'),
                     bg='#dc3545', fg='white', relief=tk.FLAT, padx=15, pady=5,
                     command=lambda t=ticket_data: self._decline_pending_ticket(t)).pack(side=tk.LEFT, padx=2)
        elif ticket_data['status'] != 'Cancelled' and 'Declined' not in ticket_data['status']:
            tk.Button(action_frame, text="❌ Cancel", font=('Arial', 9, 'bold'),
                     bg='#dc3545', fg='white', relief=tk.FLAT, padx=15, pady=5,
                     command=lambda t=ticket_data: self._cancel_ticket(t)).pack(side=tk.LEFT, padx=2)
    
    def _show_ticket_details(self, ticket_data):
        """Show detailed ticket view"""
        detail_win = tk.Toplevel(self.root)
        detail_win.title("Ticket Details")
        detail_win.geometry("500x600")
        detail_win.configure(bg='white')
        
        # Center window
        detail_win.update_idletasks()
        x = (detail_win.winfo_screenwidth() // 2) - (500 // 2)
        y = (detail_win.winfo_screenheight() // 2) - (600 // 2)
        detail_win.geometry(f"+{x}+{y}")
        
        tk.Label(detail_win, text="🎫 TICKET DETAILS", font=('Arial', 18, 'bold'),
                bg='white', fg='#007bff').pack(pady=20)
        
        ticket_text = f"""
Ticket ID: {ticket_data['ticket_id']}
Status: {ticket_data['status']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASSENGER DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {ticket_data['passenger_name']}
Age: {ticket_data['age']} years
Gender: {ticket_data['gender']}
{"Priority: YES ✅" if ticket_data['is_priority'] else "Priority: NO"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JOURNEY DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Route: {ticket_data['route'][0]} → {ticket_data['route'][1]}
Bus: {ticket_data['bus_name']}
Departure: {ticket_data['departure_time']}
{"Seat Number: " + str(ticket_data['seat_number']) if ticket_data['seat_number'] else "Waiting Queue"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAYMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Amount Paid: ₹{ticket_data['amount']}
Booking Time: {ticket_data['booking_time']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        tk.Label(detail_win, text=ticket_text, font=('Courier', 10),
                bg='white', justify=tk.LEFT).pack(padx=30, pady=20)
        
        def export_ticket():
            filename = f"ticket_{ticket_data['ticket_id']}.txt"
            with open(filename, 'w') as f:
                f.write(ticket_text)
            messagebox.showinfo("Exported", f"Ticket exported as {filename}")
        
        btn_frame = tk.Frame(detail_win, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="📥 Export", font=('Arial', 10, 'bold'),
                 bg='#28a745', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=export_ticket).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✅ Close", font=('Arial', 10, 'bold'),
                 bg='#007bff', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=detail_win.destroy).pack(side=tk.LEFT, padx=5)
    
    def _cancel_ticket(self, ticket_data):
        """Cancel a ticket"""
        result = messagebox.askyesno("Cancel Ticket", 
            f"Are you sure you want to cancel this ticket?\n\n"
            f"Ticket ID: {ticket_data['ticket_id']}\n"
            f"Passenger: {ticket_data['passenger_name']}\n"
            f"Seat: {ticket_data.get('seat_number', 'N/A')}\n"
            f"Amount: ₹{ticket_data['amount']}\n\n"
            f"Refund will be processed after cancellation.")
        
        if result:
            success, message = self.manager.cancel_ticket(ticket_data['ticket_id'])
            if success:
                messagebox.showinfo("Cancelled", message)
                # Refresh booking history
                # Close current window and reopen
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Toplevel) and "My Bookings" in widget.title():
                        widget.destroy()
                        break
                self.show_bookings()
            else:
                messagebox.showerror("Error", message)
    
    def _confirm_pending_payment(self, ticket_data):
        """Handle payment for auto-allocated seat"""
        amount = ticket_data['amount']
        
        # Create payment window
        payment_win = tk.Toplevel(self.root)
        payment_win.title("Complete Payment")
        payment_win.geometry("450x420")
        payment_win.resizable(False, False)
        payment_win.configure(bg='white')
        payment_win.grab_set()
        
        # Center window
        payment_win.update_idletasks()
        x = (payment_win.winfo_screenwidth() // 2) - (450 // 2)
        y = (payment_win.winfo_screenheight() // 2) - (420 // 2)
        payment_win.geometry(f"+{x}+{y}")
        
        tk.Label(payment_win, text="💳 Complete Your Payment", font=('Arial', 18, 'bold'),
                bg='white', fg='#007bff').pack(pady=20)
        
        tk.Label(payment_win, text=f"🎉 Good news! A seat has been allocated to you!", 
                font=('Arial', 11), bg='white', fg='#28a745').pack(pady=5)
        
        info_text = f"""
Passenger: {ticket_data['passenger_name']}
Bus: {ticket_data['bus_name']}
Route: {ticket_data['route'][0]} → {ticket_data['route'][1]}
Seat: {ticket_data['seat_number']}
        """
        tk.Label(payment_win, text=info_text, font=('Arial', 10), bg='white', justify=tk.LEFT).pack(pady=10)
        
        tk.Label(payment_win, text=f"Amount to Pay: ₹{amount}", font=('Arial', 16, 'bold'),
                bg='white', fg='#28a745').pack(pady=15)
        
        tk.Label(payment_win, text="(Simulated Payment)", font=('Arial', 10, 'italic'),
                bg='white', fg='#666').pack()
        
        def complete_payment():
            payment_win.destroy()
            # Update ticket status to Confirmed
            success, message = self.manager.confirm_pending_ticket(ticket_data['ticket_id'])
            if success:
                messagebox.showinfo("Payment Success", f"✅ Payment successful!\n\nYour seat {ticket_data['seat_number']} is now confirmed.")
                # Refresh booking history
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Toplevel) and "My Bookings" in widget.title():
                        widget.destroy()
                        break
                self.show_bookings()
            else:
                messagebox.showerror("Error", message)
        
        def cancel_payment():
            payment_win.destroy()
            messagebox.showwarning("Cancelled", "Payment cancelled. Your seat is still reserved.\nPlease complete payment to confirm your booking.")
        
        # Button frame with buttons
        btn_frame = tk.Frame(payment_win, bg='white')
        btn_frame.pack(pady=30)
        
        tk.Button(btn_frame, text="💰 Pay Now", font=('Arial', 12, 'bold'),
                 bg='#28a745', fg='white', width=12, height=2,
                 relief=tk.FLAT, command=complete_payment).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 12, 'bold'),
                 bg='#dc3545', fg='white', width=12, height=2,
                 relief=tk.FLAT, command=cancel_payment).pack(side=tk.LEFT, padx=10)
    
    def _decline_pending_ticket(self, ticket_data):
        """Decline auto-allocated seat"""
        result = messagebox.askyesno(
            "Decline Seat",
            f"Are you sure you want to decline the allocated seat?\n\n"
            f"Seat: {ticket_data['seat_number']}\n"
            f"Bus: {ticket_data['bus_name']}\n"
            f"Route: {ticket_data['route'][0]} → {ticket_data['route'][1]}\n\n"
            f"The seat will be released and may be allocated to another passenger."
        )
        
        if result:
            success, message = self.manager.decline_pending_ticket(ticket_data['ticket_id'])
            if success:
                messagebox.showinfo("Declined", "Seat allocation declined.\nThe seat has been released.")
                # Refresh booking history
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Toplevel) and "My Bookings" in widget.title():
                        widget.destroy()
                        break
                self.show_bookings()
            else:
                messagebox.showerror("Error", message)
    
    def show_admin_panel(self):
        """Show admin panel for managing buses and viewing all tickets"""
        admin_win = tk.Toplevel(self.root)
        admin_win.title("Admin Panel")
        admin_win.geometry("1200x700")
        admin_win.configure(bg='#f0f0f0')
        
        # Center window
        admin_win.update_idletasks()
        x = (admin_win.winfo_screenwidth() // 2) - (1200 // 2)
        y = (admin_win.winfo_screenheight() // 2) - (700 // 2)
        admin_win.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(admin_win, bg='#6f42c1', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="⚙️ Admin Panel", font=('Arial', 20, 'bold'),
                bg='#6f42c1', fg='white').pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Button(header, text="✕ Close", font=('Arial', 10, 'bold'),
                 bg='#dc3545', fg='white', relief=tk.FLAT, padx=15, pady=5,
                 command=admin_win.destroy).pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(admin_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: All Tickets
        tickets_frame = tk.Frame(notebook, bg='white')
        notebook.add(tickets_frame, text="📜 All Booked Tickets")
        self._create_tickets_tab(tickets_frame)
        
        # Tab 2: Manage Buses
        buses_frame = tk.Frame(notebook, bg='white')
        notebook.add(buses_frame, text="🚌 Manage Buses")
        self._create_buses_tab(buses_frame, admin_win)
    
    def _create_tickets_tab(self, parent):
        """Create tab showing all booked tickets"""
        # Header with stats
        stats_frame = tk.Frame(parent, bg='#e9ecef', height=60)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        all_tickets = self.manager.tickets
        confirmed = sum(1 for t in all_tickets if 'Confirmed' in t.get('status', ''))
        waiting = sum(1 for t in all_tickets if 'Waiting' in t.get('status', ''))
        cancelled = sum(1 for t in all_tickets if 'Cancelled' in t.get('status', '') or 'Declined' in t.get('status', ''))
        pending = sum(1 for t in all_tickets if 'Pending' in t.get('status', ''))
        
        tk.Label(stats_frame, text=f"📊 Total: {len(all_tickets)} | ✅ Confirmed: {confirmed} | ⏳ Waiting: {waiting} | 🔶 Pending: {pending} | ❌ Cancelled: {cancelled}",
                font=('Arial', 11, 'bold'), bg='#e9ecef').pack(pady=15)
        
        # Tickets list with scrollbar
        container = tk.Frame(parent, bg='white')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for tickets
        columns = ('Ticket ID', 'User', 'Passenger', 'Age', 'Bus', 'Route', 'Seat', 'Amount', 'Status', 'Booked')
        tree = ttk.Treeview(container, columns=columns, show='headings', height=20)
        
        # Configure columns
        tree.heading('Ticket ID', text='Ticket ID')
        tree.heading('User', text='User')
        tree.heading('Passenger', text='Passenger')
        tree.heading('Age', text='Age')
        tree.heading('Bus', text='Bus')
        tree.heading('Route', text='Route')
        tree.heading('Seat', text='Seat')
        tree.heading('Amount', text='Amount')
        tree.heading('Status', text='Status')
        tree.heading('Booked', text='Booked')
        
        tree.column('Ticket ID', width=100)
        tree.column('User', width=80)
        tree.column('Passenger', width=100)
        tree.column('Age', width=40)
        tree.column('Bus', width=130)
        tree.column('Route', width=130)
        tree.column('Seat', width=50)
        tree.column('Amount', width=70)
        tree.column('Status', width=150)
        tree.column('Booked', width=130)
        
        # Scrollbars
        vsb = ttk.Scrollbar(container, orient='vertical', command=tree.yview)
        hsb = ttk.Scrollbar(container, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add tickets to treeview
        for ticket in reversed(all_tickets):
            route = f"{ticket['route'][0]} → {ticket['route'][1]}"
            seat = ticket.get('seat_number', 'N/A') or 'Queue'
            tree.insert('', tk.END, values=(
                ticket['ticket_id'],
                ticket['username'],
                ticket['passenger_name'],
                ticket['age'],
                ticket['bus_name'],
                route,
                seat,
                f"₹{ticket['amount']}",
                ticket['status'],
                ticket['booking_time']
            ))
    
    def _create_buses_tab(self, parent, admin_win):
        """Create tab for managing buses"""
        # Header
        header_frame = tk.Frame(parent, bg='#e9ecef', height=50)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="Select a route to view and manage buses:", 
                font=('Arial', 11, 'bold'), bg='#e9ecef').pack(side=tk.LEFT, padx=10, pady=10)
        
        # Route selection
        route_var = tk.StringVar()
        routes = list(self.manager.buses.keys())
        route_combo = ttk.Combobox(header_frame, textvariable=route_var, values=routes, 
                                   state='readonly', width=30, font=('Arial', 10))
        route_combo.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bus list frame
        bus_container = tk.Frame(parent, bg='white')
        bus_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for buses
        columns = ('Bus ID', 'Bus Name', 'Type', 'Departure', 'Total Seats', 'Booked', 'Available', 'Price', 'Status')
        bus_tree = ttk.Treeview(bus_container, columns=columns, show='headings', height=15)
        
        for col in columns:
            bus_tree.heading(col, text=col)
            bus_tree.column(col, width=100)
        
        bus_tree.column('Bus Name', width=150)
        bus_tree.column('Bus ID', width=60)
        
        vsb = ttk.Scrollbar(bus_container, orient='vertical', command=bus_tree.yview)
        bus_tree.configure(yscrollcommand=vsb.set)
        
        bus_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons frame
        action_frame = tk.Frame(parent, bg='white')
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def load_buses(*args):
            """Load buses for selected route"""
            bus_tree.delete(*bus_tree.get_children())
            route = route_var.get()
            if route and route in self.manager.buses:
                for bus in self.manager.buses[route]:
                    booked = len(bus.booked_seats)
                    available = bus.total_seats - booked
                    status = "Active" if available > 0 else "Full"
                    bus_tree.insert('', tk.END, values=(
                        bus.bus_id,
                        bus.name,
                        bus.bus_type,
                        bus.departure_time,
                        bus.total_seats,
                        booked,
                        available,
                        f"₹{bus.base_price}",
                        status
                    ))
        
        route_combo.bind('<<ComboboxSelected>>', load_buses)
        
        def cancel_selected_bus():
            """Cancel/disable selected bus"""
            selected = bus_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a bus to cancel")
                return
            
            item = bus_tree.item(selected[0])
            bus_id = item['values'][0]
            bus_name = item['values'][1]
            
            result = messagebox.askyesno(
                "Cancel Bus",
                f"Are you sure you want to cancel this bus?\n\n"
                f"Bus: {bus_name}\n"
                f"ID: {bus_id}\n\n"
                f"All passengers will be notified and refunded."
            )
            
            if result:
                route = route_var.get()
                # Cancel all tickets for this bus
                cancelled_count = 0
                for i, ticket in enumerate(self.manager.tickets):
                    if ticket['bus_id'] == bus_id and 'Cancelled' not in ticket.get('status', ''):
                        self.manager.tickets[i]['status'] = 'Cancelled (Bus Cancelled)'
                        cancelled_count += 1
                
                # Remove bus from the route
                if route in self.manager.buses:
                    self.manager.buses[route] = [b for b in self.manager.buses[route] if b.bus_id != bus_id]
                
                self.manager._save_tickets()
                self.manager._save_buses()
                
                messagebox.showinfo("Success", f"Bus {bus_name} cancelled.\n{cancelled_count} ticket(s) have been cancelled.")
                load_buses()
        
        def view_bus_passengers():
            """View passengers for selected bus"""
            selected = bus_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a bus to view passengers")
                return
            
            item = bus_tree.item(selected[0])
            bus_id = item['values'][0]
            bus_name = item['values'][1]
            
            # Create popup window
            pass_win = tk.Toplevel(admin_win)
            pass_win.title(f"Passengers - {bus_name}")
            pass_win.geometry("800x500")
            pass_win.configure(bg='white')
            
            tk.Label(pass_win, text=f"🚌 {bus_name} - Passenger List", font=('Arial', 14, 'bold'),
                    bg='white', fg='#007bff').pack(pady=15)
            
            # Get passengers for this bus
            bus_tickets = [t for t in self.manager.tickets if t['bus_id'] == bus_id and 'Cancelled' not in t.get('status', '')]
            
            if not bus_tickets:
                tk.Label(pass_win, text="No passengers booked on this bus", font=('Arial', 12, 'italic'),
                        bg='white', fg='#666').pack(pady=50)
            else:
                # Create treeview
                columns = ('Seat', 'Passenger', 'Age', 'Status', 'Amount', 'Booked By')
                pass_tree = ttk.Treeview(pass_win, columns=columns, show='headings', height=15)
                
                for col in columns:
                    pass_tree.heading(col, text=col)
                    pass_tree.column(col, width=120)
                
                for ticket in sorted(bus_tickets, key=lambda x: x.get('seat_number') or 999):
                    pass_tree.insert('', tk.END, values=(
                        ticket.get('seat_number') or 'Queue',
                        ticket['passenger_name'],
                        ticket['age'],
                        ticket['status'],
                        f"₹{ticket['amount']}",
                        ticket['username']
                    ))
                
                pass_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            tk.Button(pass_win, text="Close", font=('Arial', 10, 'bold'),
                     bg='#6c757d', fg='white', relief=tk.FLAT, padx=20, pady=8,
                     command=pass_win.destroy).pack(pady=10)
        
        tk.Button(action_frame, text="👥 View Passengers", font=('Arial', 10, 'bold'),
                 bg='#007bff', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=view_bus_passengers).pack(side=tk.LEFT, padx=10)
        
        tk.Button(action_frame, text="❌ Cancel Bus", font=('Arial', 10, 'bold'),
                 bg='#dc3545', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=cancel_selected_bus).pack(side=tk.LEFT, padx=10)
        
        tk.Button(action_frame, text="🔄 Refresh", font=('Arial', 10, 'bold'),
                 bg='#28a745', fg='white', relief=tk.FLAT, padx=20, pady=8,
                 command=load_buses).pack(side=tk.LEFT, padx=10)
    
    def reset_form(self):
        """Reset booking form"""
        self.source_var.set("")
        self.dest_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.name_var.set("")
        self.age_var.set("")
        self.gender_var.set("Male")
        self.handicapped_var.set(False)
        self.selected_bus = None
        self.selected_seats = []
        if hasattr(self, 'passenger_linked_list'):
            self.passenger_linked_list.clear()
        self.book_btn.config(state='disabled')
        
        for widget in self.bus_list_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.bus_list_frame, text="Select route and search for buses",
                font=('Arial', 10, 'italic'), bg='white', fg='#999').pack(pady=40)
    
    def logout(self):
        """Logout user"""
        response = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if response:
            self.session.logout()
            self.main_frame.destroy()
            LoginPage(self.root, self.session, self.show_main_app)

# ==================== MAIN ====================

if __name__ == "__main__":
    print("="*60)
    print("🚌 BUS TICKET BOOKING SYSTEM")
    print("="*60)
    print("Starting application...")
    print("GUI window should appear shortly...")
    print("\nAvailable cities for booking:")
    for i, city in enumerate(BookingManager.CITIES, 1):
        print(f"  {i}. {city}")
    
    print("\nDefault login credentials:")
    print("  Username: admin  | Password: admin123")
    print("  Username: user   | Password: user123")
    
    print("\nSystem Features:")
    print("  ✓ User authentication and registration")
    print("  ✓ Multiple seat booking (Max 5 seats per booking)")
    print("  ✓ Individual passenger details for each seat")
    print("  ✓ Linked List data structure for passenger management")
    print("  ✓ Priority system: 1-Handicapped, 2-Senior(>45), 3-Normal")
    print("  ✓ Seat selection with visual interface")
    print("  ✓ Waiting queue for fully booked buses")
    print("  ✓ Ticket cancellation with auto-allocation")
    print("  ✓ Payment simulation")
    
    print("\n" + "="*60)
    print("Please check your screen for the GUI window!")
    print("="*60)
    
    root = tk.Tk()
    app = BusBookingApp(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n\nApplication closed by user.")
    except Exception as e:
        print(f"\nError occurred: {e}")
    
    print("\nThank you for using Bus Ticket Booking System!")