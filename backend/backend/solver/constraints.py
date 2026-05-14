"""
Z3 Constraint Helpers (Phase 2 Final).
Reusable math logic for geometric rules.
"""
import z3

def non_overlap_constraint(r1, r2):
    """
    Returns a Z3 constraint ensuring Rectangle 1 and Rectangle 2 do not overlap.
    Logic: Left OR Right OR Above OR Below
    """
    return z3.Or(
        r1['x'] + r1['w'] <= r2['x'],  # r1 is to the left of r2
        r2['x'] + r2['w'] <= r1['x'],  # r2 is to the left of r1
        r1['y'] + r1['h'] <= r2['y'],  # r1 is above r2
        r2['y'] + r2['h'] <= r1['y']   # r2 is above r1
    )

def adjacency_constraint(r1, r2):
    """
    Returns Z3 constraint ensuring R1 and R2 touch each other.
    """
    # 1. They must touch (distance = 0)
    touch_horizontal = z3.Or(
        r1['x'] + r1['w'] == r2['x'], # r1_right == r2_left
        r2['x'] + r2['w'] == r1['x']  # r2_right == r1_left
    )
    touch_vertical = z3.Or(
        r1['y'] + r1['h'] == r2['y'], # r1_bottom == r2_top
        r2['y'] + r2['h'] == r1['y']  # r2_bottom == r1_top
    )
    
    # 2. They must share a meaningful border (overlap range)
    # If touching horizontally, vertical ranges must overlap
    overlap_vertical = z3.And(
        r1['y'] < r2['y'] + r2['h'],
        r2['y'] < r1['y'] + r1['h']
    )
    # If touching vertically, horizontal ranges must overlap
    overlap_horizontal = z3.And(
        r1['x'] < r2['x'] + r2['w'],
        r2['x'] < r1['x'] + r1['w']
    )

    return z3.Or(
        z3.And(touch_horizontal, overlap_vertical),
        z3.And(touch_vertical, overlap_horizontal)
    )