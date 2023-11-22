import gpsd

def get_gps_data():
    # Connect to the local gpsd service (default host and port)
    gpsd.connect()

    # Get the GPS data
    packet = gpsd.get_current()

    # Check if the data is valid
    if packet.mode >= 2:
        latitude = packet.lat
        longitude = packet.lon
        altitude = packet.alt

        return(f"Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}")
    else:
        return("No GPS fix")