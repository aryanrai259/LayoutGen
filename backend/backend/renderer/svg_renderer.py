"""
SVG Renderer (Phase 3: Blueprint Style).
Generates a clean, professional floor plan for architects.
"""
import svgwrite
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SVGRenderer:
    def __init__(self, output_file="floorplan.svg", scale=50):
        """
        scale: Pixels per meter (50 px = 1m gives high resolution)
        """
        self.filename = output_file
        self.scale = scale
        
        # Style Configuration (The "Maket.ai" Look)
        self.styles = {
            "background": "#F5F5F5",      # Soft Grey Background
            "wall_stroke": "#263238",     # Dark Slate for Walls
            "wall_thickness": 3,          # Thick structural lines
            "room_fill": "#FFFFFF",       # Clean White Rooms
            "text_main": "#000000",       # Black Labels
            "text_dim": "#757575",        # Grey Dimensions
            "grid_color": "#E0E0E0"       # Light Grid
        }

    def render(self, data):
        """
        Main rendering function.
        """
        logger.info(f"🎨 Rendering blueprint to {self.filename}...")
        
        # 1. Calculate Canvas Size with Buffer
        max_w = 0
        max_h = 0
        rooms = data.get("solution", [])
        
        if not rooms:
            logger.error("❌ No rooms to render!")
            return

        for r in rooms:
            geo = r["geometry"]
            max_w = max(max_w, geo["x"] + geo["width"])
            max_h = max(max_h, geo["y"] + geo["height"])
            
        # Add padding (2 meters buffer around the plot)
        width_px = int((max_w + 4) * self.scale)
        height_px = int((max_h + 4) * self.scale)
        
        dwg = svgwrite.Drawing(self.filename, size=(width_px, height_px))
        
        # 2. Draw Background & Grid
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=self.styles["background"]))
        
        # Define Grid Pattern (1 meter squares)
        pattern = dwg.defs.add(dwg.pattern(size=(self.scale, self.scale), id="grid", patternUnits="userSpaceOnUse"))
        pattern.add(dwg.path(d=f"M {self.scale} 0 L 0 0 0 {self.scale}", 
                             stroke=self.styles["grid_color"], stroke_width=1, fill="none"))
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill="url(#grid)"))

        # 3. Draw Rooms (The "Blueprint")
        # Offset everything by 2 meters so it's centered
        offset_x = 2 * self.scale
        offset_y = 2 * self.scale
        
        # Group for room shapes
        room_group = dwg.add(dwg.g(id="rooms"))
        
        for room in rooms:
            rid = room["id"]
            geo = room["geometry"]
            
            x = geo["x"] * self.scale + offset_x
            y = geo["y"] * self.scale + offset_y
            w = geo["width"] * self.scale
            h = geo["height"] * self.scale
            
            # A. Draw Room Rectangle (White Fill, Dark Stroke)
            room_group.add(dwg.rect(
                insert=(x, y), 
                size=(w, h), 
                fill=self.styles["room_fill"], 
                stroke=self.styles["wall_stroke"], 
                stroke_width=self.styles["wall_thickness"]
            ))
            
            # B. Draw Labels
            cx = x + w/2
            cy = y + h/2
            
            # Room Name (Bold, Black)
            room_group.add(dwg.text(
                rid.replace("_", " ").title(), 
                insert=(cx, cy - 5), 
                text_anchor="middle", 
                font_size="14px", 
                font_family="Segoe UI, Helvetica, Arial", 
                font_weight="bold",
                fill=self.styles["text_main"]
            ))
            
            # Dimensions (Small, Grey)
            dim_text = f"{geo['width']:.2f}m x {geo['height']:.2f}m"
            room_group.add(dwg.text(
                dim_text, 
                insert=(cx, cy + 15), 
                text_anchor="middle", 
                font_size="11px", 
                font_family="Consolas, monospace", 
                fill=self.styles["text_dim"]
            ))
            
            # Area (Tiny, Grey)
            area_text = f"({geo['width'] * geo['height']:.1f} m²)"
            room_group.add(dwg.text(
                area_text, 
                insert=(cx, cy + 30), 
                text_anchor="middle", 
                font_size="10px", 
                font_family="Consolas, monospace", 
                fill="#9E9E9E"
            ))

        # 4. Save
        dwg.save()
        logger.info("✅ Blueprint Saved Successfully.")