from datetime import datetime, timezone
from src.generated import FlightState, TelemetryPacket

def flight_state_name(state: FlightState) -> str:
    state_names = {
        FlightState.STANDBY: "STANDBY",
        FlightState.ASCENT: "ASCENT",
        FlightState.MACH_LOCK: "MACH_LOCK",
        FlightState.DROGUE_DESCENT: "DROGUE_DESCENT",
        FlightState.MAIN_DESCENT: "MAIN_DESCENT",
        FlightState.LANDED: "LANDED",
    }
    return state_names.get(state, f"UNKNOWN_{state}")

def format_telemetry_packet(data: TelemetryPacket) -> dict:
    formatted_packet = {
        "time": datetime.now(timezone.utc),
        "flight_state": data.state,
        # Packet metadata
        "counter": data.counter,
        "timestamp_ms": data.timestamp_ms,
        "state": data.state,
        # IMU data
        "accel_x": data.accel_x,
        "accel_y": data.accel_y,
        "accel_z": data.accel_z,
        "gyro_x": data.gyro_x,
        "gyro_y": data.gyro_y,
        "gyro_z": data.gyro_z,
        # Kalman filter estimates
        "kf_altitude": data.kf_altitude,
        "kf_velocity": data.kf_velocity,
        "kf_alt_variance": data.kf_alt_variance,
        "kf_vel_variance": data.kf_vel_variance,
        # Barometer 0 data
        "baro0_healthy": data.baro0_healthy,
        "baro0_pressure": data.baro0_pressure,
        "baro0_temperature": data.baro0_temperature,
        "baro0_altitude": data.baro0_altitude,
        "baro0_nis": data.baro0_nis,
        "baro0_faults": data.baro0_faults,
        # Barometer 1 data
        "baro1_healthy": data.baro1_healthy,
        "baro1_pressure": data.baro1_pressure,
        "baro1_temperature": data.baro1_temperature,
        "baro1_altitude": data.baro1_altitude,
        "baro1_nis": data.baro1_nis,
        "baro1_faults": data.baro1_faults,
        # GPS data
        "gps_latitude": data.gps_latitude,
        "gps_longitude": data.gps_longitude,
        "gps_altitude": data.gps_altitude,
        "gps_speed": data.gps_speed,
        "gps_sats": data.gps_sats,
        "gps_fix": data.gps_fix
    }

    return formatted_packet

# def format_aprs_packet(data: AprsPacket) -> dict:
#     pos = data.position
#     formatted_packet = {
#         "time": datetime.now(timezone.utc),
#         "callsign": data.source,
#         "gps_latitude": pos.latitude,
#         "gps_longitude": pos.longitude
#     }

#     return formatted_packet