"""
Z3 Floor Plan Solver (Phase 11: The Iron Box).
Combines STRICT Plot Limits (to prevent sprawl) with SHARED WALLS (to ensure doors).
"""
from z3 import *
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Z3FloorPlanSolver:
    def __init__(self, semantic_layout: Dict[str, Any], enable_grid_snapping: bool = True):
        self.layout = semantic_layout
        self.opt = Optimize()
        self.opt.set(priority="lex") 
        self.opt.set("timeout", 15000)  # 15s timeout (Performance fix)
        self.opt.set("enable_sat", True)  # Enable SAT mode for speed
        self.room_vars = {}
        self.grid_size = 0.5 

    def solve(self):
        return self.solve_layout(self.layout)

    def solve_layout(self, layout_data=None):
        if layout_data: self.layout = layout_data
        logger.info("--- 🧮 Starting Z3 'Iron Box' Solver ---")
        
        self._create_variables()
        self._add_grid_constraints()
        
        # 1. THE IRON BOX: Strict Plot Limits
        self._add_strict_boundaries()
        
        # 2. THE DOOR MAKER: Force 1m Overlap
        self._add_strict_shared_wall_adjacency()
        
        self._add_size_constraints()
        self._add_maximum_constraints()
        self._add_aspect_ratios()
        self._add_non_overlap()
        
        # Objectives
        self._add_bounding_box_minimization()
        self._add_alignment()
        self._add_vaastu()
        
        logger.info("Solving for tight packing with valid doors...")
        status = self.opt.check()
        
        if status == sat:
            logger.info("✅ SATISFIABLE: Perfect layout found!")
            return self._extract_solution()
        elif status == unknown:
            logger.warning("⚠️ TIMEOUT: Returning best effort.")
            try: return self._extract_solution()
            except: return {"status": "failure", "reason": "Timeout"}
        else:
            logger.error("❌ UNSATISFIABLE. Plot too small for these rooms.")
            return {"status": "failure", "reason": "Plot too small"}

    def _create_variables(self):
        for room in self.layout.get("rooms", []):
            rid = room["id"]
            self.room_vars[rid] = {
                'x': Real(f"{rid}_x"), 'y': Real(f"{rid}_y"),
                'w': Real(f"{rid}_w"), 'h': Real(f"{rid}_h")
            }
            v = self.room_vars[rid]
            self.opt.add(v['w'] > 0.5, v['h'] > 0.5, v['x'] >= 0, v['y'] >= 0)

    def _add_grid_constraints(self):
        for rid, v in self.room_vars.items():
            ix, iy, iw, ih = Int(f"{rid}_ix"), Int(f"{rid}_iy"), Int(f"{rid}_iw"), Int(f"{rid}_ih")
            self.opt.add(v['x'] == ix * self.grid_size)
            self.opt.add(v['y'] == iy * self.grid_size)
            self.opt.add(v['w'] == iw * self.grid_size)
            self.opt.add(v['h'] == ih * self.grid_size)

    def _add_strict_boundaries(self):
        """
        HARD LIMIT: Rooms CANNOT go outside the user's plot.
        This kills the 'Cross Shape' sprawl.
        """
        meta = self.layout.get("project_meta", {})
        # Default to 15x12 if missing. 
        # Crucial: These must match your test_phase2.py request!
        PLOT_W = meta.get("plot_width", 12.0)
        PLOT_L = meta.get("plot_length", 15.0)
        
        logger.info(f"🔒 Enforcing Strict Limits: {PLOT_W}m x {PLOT_L}m")
        
        for v in self.room_vars.values():
            self.opt.add(v['x'] + v['w'] <= PLOT_W)
            self.opt.add(v['y'] + v['h'] <= PLOT_L)

    def _add_size_constraints(self):
        for room in self.layout.get("rooms", []):
            rid = room["id"]
            v = self.room_vars[rid]
            legal = room.get("legal", {})
            min_area = legal.get("min_area", 4.0)
            self.opt.add(v['w'] * v['h'] >= min_area)
            self.opt.add(v['w'] >= legal.get("min_width", 1.5))
            self.opt.add(v['h'] >= legal.get("min_width", 1.5))

    def _add_maximum_constraints(self):
        for room in self.layout.get("rooms", []):
            rid = room["id"]
            rtype = room.get("type", "").lower()
            v = self.room_vars[rid]
            legal = room.get("legal", {})
            min_area = legal.get("min_area", 4.0)
            
            if "bath" in rtype:
                self.opt.add(v['w'] * v['h'] <= 6.0) 
            elif "corridor" in rtype:
                self.opt.add(v['w'] * v['h'] <= 12.0)
            else:
                self.opt.add(v['w'] * v['h'] <= min_area * 3.0)

    def _add_aspect_ratios(self):
        for room in self.layout.get("rooms", []):
            v = self.room_vars[room["id"]]
            rtype = room["type"].lower()
            if "corridor" in rtype:
                self.opt.add(v['w'] <= 6.0 * v['h'])
                self.opt.add(v['h'] <= 6.0 * v['w'])
            else:
                self.opt.add(v['w'] <= 2.0 * v['h'])
                self.opt.add(v['h'] <= 2.0 * v['w'])

    def _add_non_overlap(self):
        ids = list(self.room_vars.keys())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                v1, v2 = self.room_vars[ids[i]], self.room_vars[ids[j]]
                self.opt.add(Or(
                    v1['x'] + v1['w'] <= v2['x'], v2['x'] + v2['w'] <= v1['x'],
                    v1['y'] + v1['h'] <= v2['y'], v2['y'] + v2['h'] <= v1['y']
                ))

    def _add_strict_shared_wall_adjacency(self):
        """
        Calculates exact overlap length using Min/Max logic.
        Forces Overlap >= 1.0 meter for every connection.
        """
        for pair in self.layout.get("adjacencies", []):
            if len(pair) < 2: continue
            id1, id2 = pair[0], pair[1]
            if id1 in self.room_vars and id2 in self.room_vars:
                v1, v2 = self.room_vars[id1], self.room_vars[id2]
                
                # 1. Distance must be zero (Touching)
                dist_x = If(v1['x'] + v1['w'] < v2['x'], v2['x'] - (v1['x'] + v1['w']),
                            If(v2['x'] + v2['w'] < v1['x'], v1['x'] - (v2['x'] + v2['w']), 0))
                dist_y = If(v1['y'] + v1['h'] < v2['y'], v2['y'] - (v1['y'] + v1['h']),
                            If(v2['y'] + v2['h'] < v1['y'], v1['y'] - (v2['y'] + v2['h']), 0))
                self.opt.add(dist_x + dist_y == 0)
                
                # 2. Calculate Overlap Length
                # X Overlap = Min(Ends) - Max(Starts)
                start_x = If(v1['x'] > v2['x'], v1['x'], v2['x'])
                end_x = If(v1['x'] + v1['w'] < v2['x'] + v2['w'], v1['x'] + v1['w'], v2['x'] + v2['w'])
                overlap_x = end_x - start_x
                
                # Y Overlap
                start_y = If(v1['y'] > v2['y'], v1['y'], v2['y'])
                end_y = If(v1['y'] + v1['h'] < v2['y'] + v2['h'], v1['y'] + v1['h'], v2['y'] + v2['h'])
                overlap_y = end_y - start_y
                
                # Constraint: Must overlap by 1m in EITHER direction
                self.opt.add(Or(overlap_x >= 1.0, overlap_y >= 1.0))

    def _add_bounding_box_minimization(self):
        max_x, max_y = Real('bbox_max_x'), Real('bbox_max_y')
        for v in self.room_vars.values():
            self.opt.add(v['x'] + v['w'] <= max_x)
            self.opt.add(v['y'] + v['h'] <= max_y)
        self.opt.minimize(max_x + max_y)

    def _add_alignment(self):
        ids = list(self.room_vars.keys())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                v1, v2 = self.room_vars[ids[i]], self.room_vars[ids[j]]
                self.opt.minimize(If(v1['x'] > v2['x'], v1['x'] - v2['x'], v2['x'] - v1['x']))
                self.opt.minimize(If(v1['y'] > v2['y'], v1['y'] - v2['y'], v2['y'] - v1['y']))

    def _add_vaastu(self):
        """
        Maps Compass Directions (N, S, E, W) to actual Grid Coordinates.
        For Entrance rooms: Apply HARD boundary constraints.
        For other rooms: Apply SOFT constraints (minimize distance).
        """
        meta = self.layout.get("project_meta", {})
        W = float(meta.get("plot_width", 12.0))
        L = float(meta.get("plot_length", 15.0))
        orientation = meta.get("orientation", "N").upper()
        
        # 🧭 COORDINATE MAPPING (0,0 is bottom-left, x=width, y=length)
        ZONES = {
            "N":  (W/2, L),    "S":  (W/2, 0),
            "E":  (W, L/2),    "W":  (0, L/2),
            "NE": (W, L),      "NW": (0, L),
            "SE": (W, 0),      "SW": (0, 0),
            "CENTER": (W/2, L/2)
        }

        for room in self.layout.get("rooms", []):
            rid = room["id"]
            if rid not in self.room_vars: continue

            rtype = room.get("type", "").lower()
            v = self.room_vars[rid]

            # Get Preferred Zones
            preferred_zones = room.get("vaastu", {}).get("preferred_zones", [])
            
            # SPECIAL CASE: Entrance room - apply HARD boundary constraints
            if rtype == "entrance":
                # Use orientation from project_meta, or first preferred zone
                entrance_zone = orientation if orientation in ["N", "S", "E", "W"] else (preferred_zones[0] if preferred_zones else "N")
                
                logger.info(f"🚪 Applying HARD boundary constraint for Entrance: {entrance_zone}")
                
                if entrance_zone == "N":
                    # Snap to North edge: y == 0 (top edge)
                    self.opt.add(v['y'] == 0)
                elif entrance_zone == "S":
                    # Snap to South edge: y == plot_length - room_height (bottom edge)
                    self.opt.add(v['y'] == L - v['h'])
                elif entrance_zone == "E":
                    # Snap to East edge: x == plot_width - room_width (right edge)
                    self.opt.add(v['x'] == W - v['w'])
                elif entrance_zone == "W":
                    # Snap to West edge: x == 0 (left edge)
                    self.opt.add(v['x'] == 0)
                
                # Also apply soft constraint for fine-tuning
                if preferred_zones:
                    cx, cy = v['x'] + v['w']/2, v['y'] + v['h']/2
                    constraints = []
                    for zone in preferred_zones:
                        if zone in ZONES:
                            tx, ty = ZONES[zone]
                            constraints.append((cx - tx)**2 + (cy - ty)**2)
                    if constraints:
                        self.opt.minimize(sum(constraints) * 100)
                continue

            # OTHER ROOMS: Apply SOFT constraints (minimize distance to preferred zones)
            if not preferred_zones: continue

            cx, cy = v['x'] + v['w']/2, v['y'] + v['h']/2

            # Create magnetic pull towards the correct zone
            constraints = []
            for zone in preferred_zones:
                if zone in ZONES:
                    tx, ty = ZONES[zone]
                    # Minimize Distance^2
                    constraints.append((cx - tx)**2 + (cy - ty)**2)
            
            if constraints:
                # Add as a Soft Constraint (Strong Weight = 100 for entrance orientation)
                self.opt.minimize(sum(constraints) * 100)

    def _extract_solution(self):
        m = self.opt.model()
        solution = []
        for room in self.layout["rooms"]:
            rid = room["id"]
            v = self.room_vars[rid]
            def to_float(x):
                val = m.eval(x)
                if isinstance(val, RatNumRef):
                    return float(val.numerator_as_long()) / float(val.denominator_as_long())
                try: return float(val.as_decimal(10).replace("?", ""))
                except: return 0.0
            solution.append({
                "id": rid, "type": room["type"],
                "geometry": { "x": to_float(v['x']), "y": to_float(v['y']),
                              "width": to_float(v['w']), "height": to_float(v['h']) }
            })
        return { "status": "success", "solution": solution, "adjacencies": self.layout.get("adjacencies", []) }