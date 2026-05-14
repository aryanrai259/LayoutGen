"""
Validation utilities module.
Helper functions for validating floor plan constraints and inputs.
"""

from typing import Dict, Any, List, Tuple


def validate_room_dimensions(room: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate room dimensions are positive and reasonable.
    
    Args:
        room: Room dictionary with width, height, area
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    width = room.get("width", 0)
    height = room.get("height", 0)
    area = room.get("area", 0)
    
    if width <= 0:
        return False, "Room width must be positive"
    if height <= 0:
        return False, "Room height must be positive"
    if area <= 0:
        return False, "Room area must be positive"
    
    # Check if area matches dimensions
    calculated_area = width * height
    if abs(calculated_area - area) > 0.01:
        return False, f"Room area {area} does not match dimensions {width} x {height}"
    
    return True, ""


def validate_no_overlaps(rooms: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Validate that rooms do not overlap.
    
    Args:
        rooms: List of room dictionaries with x, y, width, height
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            r1 = rooms[i]
            r2 = rooms[j]
            
            r1_x1, r1_y1 = r1.get("x", 0), r1.get("y", 0)
            r1_x2 = r1_x1 + r1.get("width", 0)
            r1_y2 = r1_y1 + r1.get("height", 0)
            
            r2_x1, r2_y1 = r2.get("x", 0), r2.get("y", 0)
            r2_x2 = r2_x1 + r2.get("width", 0)
            r2_y2 = r2_y1 + r2.get("height", 0)
            
            # Check for overlap
            if not (r1_x2 <= r2_x1 or r2_x2 <= r1_x1 or r1_y2 <= r2_y1 or r2_y2 <= r1_y1):
                return False, f"Rooms {r1.get('room_type')} and {r2.get('room_type')} overlap"
    
    return True, ""


def validate_within_plot(rooms: List[Dict[str, Any]], plot_length: float, plot_width: float) -> Tuple[bool, str]:
    """
    Validate that all rooms are within plot boundaries.
    
    Args:
        rooms: List of room dictionaries
        plot_length: Plot length
        plot_width: Plot width
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    for room in rooms:
        x = room.get("x", 0)
        y = room.get("y", 0)
        width = room.get("width", 0)
        height = room.get("height", 0)
        
        if x < 0 or y < 0:
            return False, f"Room {room.get('room_type')} has negative position"
        if x + width > plot_length:
            return False, f"Room {room.get('room_type')} exceeds plot length"
        if y + height > plot_width:
            return False, f"Room {room.get('room_type')} exceeds plot width"
    
    return True, ""


def validate_geometric_layout(geometric_layout: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Comprehensive validation of geometric layout.
    
    Args:
        geometric_layout: Complete geometric layout dictionary
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    rooms = geometric_layout.get("rooms", [])
    plot_length = geometric_layout.get("plot_length", 0)
    plot_width = geometric_layout.get("plot_width", 0)
    
    if plot_length <= 0 or plot_width <= 0:
        errors.append("Plot dimensions must be positive")
    
    for room in rooms:
        is_valid, error = validate_room_dimensions(room)
        if not is_valid:
            errors.append(error)
    
    is_valid, error = validate_no_overlaps(rooms)
    if not is_valid:
        errors.append(error)
    
    is_valid, error = validate_within_plot(rooms, plot_length, plot_width)
    if not is_valid:
        errors.append(error)
    
    return len(errors) == 0, errors

