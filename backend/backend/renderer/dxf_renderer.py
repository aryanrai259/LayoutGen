"""
DXF Renderer (Professional CAD Export).
Converts the generated layout into an editable .dxf file for AutoCAD/Revit.
"""
import logging
import ezdxf
from ezdxf.addons import drawing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DXFRenderer:
    def __init__(self, output_file="floorplan.dxf"):
        self.filename = output_file
        
    def render(self, data):
        logger.info(f"🏗️ Exporting CAD file to {self.filename}...")
        
        rooms = data.get("solution", [])
        adjacencies = data.get("adjacencies", [])
        
        if not rooms:
            logger.warning("⚠️ No rooms to export.")
            return

        # 1. Create a new DXF document (R2010 version is safe standard)
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # 2. Setup Layers (AutoCAD Layers)
        doc.layers.new(name='A-WALL', dxfattribs={'color': 7}) # White/Black
        doc.layers.new(name='A-DOOR', dxfattribs={'color': 3}) # Green
        doc.layers.new(name='A-FURN', dxfattribs={'color': 8}) # Grey
        doc.layers.new(name='A-TEXT', dxfattribs={'color': 7})
        
        # 3. Draw Rooms (Walls)
        for room in rooms:
            geo = room["geometry"]
            # DXF uses direct units (Meters)
            points = [
                (geo["x"], geo["y"]),
                (geo["x"] + geo["width"], geo["y"]),
                (geo["x"] + geo["width"], geo["y"] + geo["height"]),
                (geo["x"], geo["y"] + geo["height"]),
                (geo["x"], geo["y"]) # Close loop
            ]
            msp.add_lwpolyline(points, dxfattribs={'layer': 'A-WALL', 'lineweight': 30})
            
            # Add Text Labels
            cx = geo["x"] + geo["width"]/2
            cy = geo["y"] + geo["height"]/2
            
            # Room Name
            msp.add_text(
                room["id"].replace("_", " ").upper(), 
                dxfattribs={'layer': 'A-TEXT', 'height': 0.25}
            ).set_placement((cx, cy), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
            
            # Dimensions
            dim_text = f"{geo['width']:.2f}m x {geo['height']:.2f}m"
            msp.add_text(
                dim_text,
                dxfattribs={'layer': 'A-TEXT', 'height': 0.15}
            ).set_placement((cx, cy - 0.35), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

        # 4. Draw Doors (Cuts)
        # In DXF, we usually draw a simple line or arc for doors
        for pair in adjacencies:
            self._draw_door_dxf(msp, pair, rooms)

        # 5. Save
        doc.saveas(self.filename)
        logger.info(f"✅ DXF Export Complete: {self.filename}")

    def _draw_door_dxf(self, msp, pair, rooms):
        # Find room objects
        r1 = next((r for r in rooms if r["id"] == pair[0]), None)
        r2 = next((r for r in rooms if r["id"] == pair[1]), None)
        if not r1 or not r2: return
        
        g1, g2 = r1["geometry"], r2["geometry"]
        
        # Determine overlap center
        # Vertical Wall
        overlap_y_start = max(g1["y"], g2["y"])
        overlap_y_end = min(g1["y"] + g1["height"], g2["y"] + g2["height"])
        
        # Horizontal Wall
        overlap_x_start = max(g1["x"], g2["x"])
        overlap_x_end = min(g1["x"] + g1["width"], g2["x"] + g2["width"])
        
        door_size = 0.9
        
        if (overlap_y_end - overlap_y_start) > 0.5:
            # Vertical Door
            mid_y = (overlap_y_start + overlap_y_end) / 2
            shared_x = g1["x"] if abs(g1["x"] - (g2["x"] + g2["width"])) < 0.1 else g2["x"]
            
            # Draw Door Swing (Arc representation)
            msp.add_arc(
                center=(shared_x, mid_y - door_size/2),
                radius=door_size,
                start_angle=0,
                end_angle=90,
                dxfattribs={'layer': 'A-DOOR'}
            )
            # Draw Door Leaf (Line)
            msp.add_line(
                (shared_x, mid_y - door_size/2),
                (shared_x, mid_y + door_size/2),
                dxfattribs={'layer': 'A-DOOR'}
            )

        elif (overlap_x_end - overlap_x_start) > 0.5:
            # Horizontal Door
            mid_x = (overlap_x_start + overlap_x_end) / 2
            shared_y = g1["y"] if abs(g1["y"] - (g2["y"] + g2["height"])) < 0.1 else g2["y"]
            
            # Draw Door Swing
            msp.add_arc(
                center=(mid_x - door_size/2, shared_y),
                radius=door_size,
                start_angle=0,
                end_angle=90,
                dxfattribs={'layer': 'A-DOOR'}
            )
            # Door Leaf
            msp.add_line(
                (mid_x - door_size/2, shared_y),
                (mid_x + door_size/2, shared_y),
                dxfattribs={'layer': 'A-DOOR'}
            )