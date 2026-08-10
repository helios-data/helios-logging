from datetime import datetime, timezone
from src.generated import FlightState, TelemetryPacket
from helios.generated.helios.transport import AprsPacket

# Temp protos
from src.generated_temp.helios.transport import NmeaPosition, NmeaSentence
from src.generated_temp import LandingPoint, LandingPrediction

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
        "time": datetime.now(timezone.utc).timestamp(),
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
        "gps_fix": data.gps_fix,
    }

    return formatted_packet

def format_aprs_packet(data: AprsPacket) -> dict:
    pos = data.position
    formatted_packet = {
        "time": datetime.now(timezone.utc).timestamp(),
        "callsign": data.source,
        "gps_latitude": pos.latitude if pos else None,
        "gps_longitude": pos.longitude if pos else None,
    }

    return formatted_packet

def format_nmea_sentence(data: NmeaSentence) -> dict:
    formatted_packet = {
        "time": datetime.now(timezone.utc).timestamp(),
        "talker_id": data.talker_id,
        "sentence_type": data.sentence_type,
        "timestamp": str(data.timestamp),
        "checksum_valid": data.checksum_valid,
        "position": _format_nmea_position(data.position) if data.position else None,
        "raw_sentence": data.raw_sentence,
    }

    return formatted_packet

def format_landing_prediction(data: LandingPrediction) -> dict:
    formatted_packet = {
        "time": datetime.now(timezone.utc).timestamp(),
        "based_on_packet_counter": data.based_on_packet_counter,
        "computed_at_ms": data.computed_at_ms,
        "final": data.final,
        "best_estimate": _format_landing_point(data.best_estimate) if data.best_estimate else None,
        "dispersion_cloud": [_format_landing_point(point) for point in data.dispersion_cloud],
        "ellipse_50": [_format_landing_point(point) for point in data.ellipse_50],
        "ellipse_90": [_format_landing_point(point) for point in data.ellipse_90],
        "current_lat": data.current_lat,
        "current_lon": data.current_lon,
        "current_source": data.current_source,
        "wind_source": data.wind_source,
        "descent_model": data.descent_model,
        "current_alt_agl": data.current_alt_agl,
        "flight_state": data.flight_state,
        "status": data.status,
    }

    return formatted_packet

def _format_landing_point(point: LandingPoint) -> dict:
    return {
        "lat": point.lat,
        "lon": point.lon,
    }

def _format_nmea_position(pos: NmeaPosition) -> dict:
    return {
        "latitude": pos.latitude,
        "longitude": pos.longitude,
        "altitude_m": pos.altitude_m,
        "speed_knots": pos.speed_knots,
        "course_deg": pos.course_deg,
        "fix_quality": pos.fix_quality,
        "geoid_separation_m": pos.geoid_separation_m,
        "hdop": pos.hdop,
        "satellites_used": pos.satellites_used,
    }
