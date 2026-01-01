# Bus Booking System Using Python

A comprehensive console-based bus booking system built with Python that allows users to search for bus routes, book tickets, cancel bookings, and manage bus operations.

## Features

### For Passengers:
- 🔍 **Search Routes**: Find available bus routes between cities
- 🎫 **Book Tickets**: Reserve seats on available buses
- 📋 **View Bookings**: Check booking details using booking ID
- ❌ **Cancel Bookings**: Cancel existing bookings and get seat refund
- 🚌 **View Available Buses**: See all available buses on a specific route

### For Administrators:
- ➕ **Add Routes**: Create new bus routes with source and destination
- 🚐 **Add Buses**: Add buses to existing routes with fare details
- 💾 **Data Persistence**: All data is automatically saved to JSON file

## Installation

### Prerequisites
- Python 3.6 or higher

### Setup
1. Clone the repository:
```bash
git clone https://github.com/Sushanthnayak-eng/Bus_Booking_system_Using_Pyhton.git
cd Bus_Booking_system_Using_Pyhton
```

2. No additional dependencies required - uses only Python standard library!

## Usage

### Running the Application
```bash
python bus_booking_system.py
```

### Menu Options

```
1. View Available Routes       - Display all routes in the system
2. Search Routes               - Find routes between specific cities
3. View Available Buses        - See buses on a particular route
4. Book a Ticket              - Make a new booking
5. Cancel Booking             - Cancel an existing booking
6. View Booking Details       - Check details of a booking
7. Add Route (Admin)          - Add a new route to the system
8. Add Bus to Route (Admin)   - Add a bus to an existing route
9. Exit                       - Close the application
```

## Example Usage

### Booking a Ticket

1. Select option `2` to search routes
   - Enter source city: `Mumbai`
   - Enter destination city: `Pune`

2. Select option `3` to view available buses
   - Enter route ID: `R001`
   - View available buses and their seat availability

3. Select option `4` to book a ticket
   - Enter route ID: `R001`
   - Enter bus ID: `B001`
   - Enter seat number: `15`
   - Enter passenger name: `John Doe`
   - Enter phone number: `9876543210`

4. You'll receive a booking confirmation with your unique Booking ID

### Cancelling a Booking

1. Select option `5`
2. Enter your booking ID (e.g., `BK0001`)
3. Booking will be cancelled and seat will be released

## Data Storage

The system automatically saves all data to `booking_data.json` in the same directory. This includes:
- All routes and their details
- All buses and their seat information
- All bookings and their status

## Sample Data

The system comes pre-loaded with sample data:

| Route ID | From      | To        | Distance |
|----------|-----------|-----------|----------|
| R001     | Mumbai    | Pune      | 150 km   |
| R002     | Delhi     | Jaipur    | 280 km   |
| R003     | Bangalore | Mysore    | 145 km   |

Sample buses include Volvo AC, Mercedes Sleeper, Scania Multi-Axle, and Ashok Leyland AC with varying seat capacities and fares.

## Code Structure

- **Bus Class**: Manages individual bus details and seat booking
- **Route Class**: Handles route information and associated buses
- **Booking Class**: Stores passenger booking information
- **BusBookingSystem Class**: Main system class that orchestrates all operations
- **Data Persistence**: Automatic save/load functionality using JSON

## Features in Detail

### Smart Seat Management
- Real-time seat availability tracking
- Prevents double booking of seats
- Automatic seat release on cancellation

### Input Validation
- Validates all user inputs
- Handles invalid route IDs, bus IDs, and seat numbers
- Provides clear error messages

### Data Persistence
- Automatic saving after every booking/cancellation
- Loads existing data on startup
- Maintains booking counter across sessions

## Future Enhancements

Potential improvements for future versions:
- Date-based booking system
- Multiple journey dates
- User authentication system
- Payment integration
- Email/SMS notifications
- Seat selection GUI
- Ticket PDF generation
- Booking history for passengers

## Contributing

Feel free to fork this repository and submit pull requests for any improvements.

## License

This project is open-source and available for educational purposes.

## Author

Sushanthnayak-eng

## Support

For issues or questions, please open an issue on the GitHub repository.