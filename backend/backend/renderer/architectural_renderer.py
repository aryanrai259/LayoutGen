"""
Architectural Renderer (Final + Main Door Fix).
"""
import svgwrite
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArchitecturalRenderer:
    def __init__(self, output_file="floorplan_maket.svg", scale=60):
        self.filename = output_file
        self.scale = scale 
        self.styles = {
            "canvas_bg": "#FFFFFF",
            "wall_color": "#000000",
            "wall_width": 4,
            "door_color": "#000000",
            "room_fill": "#FFFFFF",
            "text_color": "#000000",
            "grid_color": "#E8E8E8",
            "furniture_stroke": "#A0A0A0",
            "furniture_width": 2, 
            "furniture_fill": "none"
        }

    def _meters_to_feet(self, meters):
        total_inches = meters * 39.3701
        feet = int(total_inches // 12)
        inches = int(total_inches % 12)
        return f"{feet}' {inches}\""

    def render(self, data):
        logger.info(f"🎨 Rendering plan with MAIN DOOR to {self.filename}...")
        
        rooms = data.get("solution", [])
        adjacencies = data.get("adjacencies", [])
        
        if not rooms: return

        # Canvas setup
        max_w = max([r["geometry"]["x"] + r["geometry"]["width"] for r in rooms])
        max_h = max([r["geometry"]["y"] + r["geometry"]["height"] for r in rooms])
        
        width_px = int((max_w + 4) * self.scale) # Extra padding for labels
        height_px = int((max_h + 4) * self.scale)
        
        dwg = svgwrite.Drawing(self.filename, size=('100%', '100%'))
        dwg.viewbox(0, 0, width_px, height_px)
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=self.styles["canvas_bg"]))

        # Grid
        pattern = dwg.defs.add(dwg.pattern(size=(30, 30), id="grid", patternUnits="userSpaceOnUse"))
        pattern.add(dwg.path(d="M 30 0 L 0 0 0 30", stroke=self.styles["grid_color"], fill="none"))
        dwg.add(dwg.rect(size=('100%', '100%'), fill="url(#grid)"))

        # Center layout
        offset_x = 2 * self.scale
        offset_y = 2 * self.scale
        
        # Furniture
        for room in rooms:
            self._draw_furniture(dwg, room, offset_x, offset_y)

        # Walls
        for room in rooms:
            geo = room["geometry"]
            x = geo["x"] * self.scale + offset_x
            y = geo["y"] * self.scale + offset_y
            w = geo["width"] * self.scale
            h = geo["height"] * self.scale
            
            dwg.add(dwg.rect((x, y), (w, h), 
                             fill="none", 
                             stroke=self.styles["wall_color"], 
                             stroke_width=self.styles["wall_width"]))

        # Internal Doors
        for pair in adjacencies:
            r1 = next((r for r in rooms if r["id"] == pair[0]), None)
            r2 = next((r for r in rooms if r["id"] == pair[1]), None)
            if r1 and r2:
                self._draw_door_between(dwg, r1, r2, offset_x, offset_y)

        # MAIN ENTRANCE DOOR (The Fix)
        for room in rooms:
            if "entrance" in room["type"].lower() or "entry" in room["id"].lower():
                self._draw_main_entry(dwg, room, offset_x, offset_y)
        
        # Labels
        for room in rooms:
            self._draw_labels(dwg, room, offset_x, offset_y)

        dwg.save()
        logger.info("✅ Fixed SVG saved.")

    def _draw_main_entry(self, dwg, room, off_x, off_y):
        """Draws a main double-door or arrow on the Entrance room."""
        geo = room["geometry"]
        x = geo["x"] * self.scale + off_x
        y = geo["y"] * self.scale + off_y
        w = geo["width"] * self.scale
        h = geo["height"] * self.scale
        
        # We assume main entry is at the "Bottom" or "Right" based on typical bounding
        # For simplicity, we draw it on the Bottom Wall of the Entrance Room
        door_w = 1.2 * self.scale
        if door_w > w: door_w = w * 0.8
        
        dx = x + w/2 - door_w/2
        dy = y + h # Bottom edge
        
        # 1. Clear Wall
        dwg.add(dwg.rect((dx, dy - 2), (door_w, 4), fill="white"))
        
        # 2. Draw Door Step
        dwg.add(dwg.rect((dx, dy + 2), (door_w, 4), fill="#CCCCCC"))
        
        # 3. Draw "Main Entry" Arrow
        ax = dx + door_w/2
        ay = dy + 15
        dwg.add(dwg.path(d=f"M {ax},{ay+10} L {ax},{ay} L {ax-3},{ay+3} M {ax},{ay} L {ax+3},{ay+3}", 
                         stroke="black", stroke_width=2, fill="none"))

    def _draw_furniture(self, dwg, room, off_x, off_y):
        rtype = room["type"].lower()
        geo = room["geometry"]
        x = geo["x"] * self.scale + off_x
        y = geo["y"] * self.scale + off_y
        w = geo["width"] * self.scale
        h = geo["height"] * self.scale
        cx, cy = x + w/2, y + h/2
        
        stroke = self.styles["furniture_stroke"]
        sw = self.styles["furniture_width"]

        if "bed" in rtype:
            bw, bh = 1.6 * self.scale, 2.0 * self.scale
            if bw > w * 0.9: bw = w * 0.8
            if bh > h * 0.9: bh = h * 0.8
            bx, by = cx - bw/2, cy - bh/2
            dwg.add(dwg.rect((bx, by), (bw, bh), rx=5, ry=5, stroke=stroke, stroke_width=sw, fill="none"))
            dwg.add(dwg.line((bx, by + bh*0.2), (bx+bw, by + bh*0.2), stroke=stroke))

        elif "dining" in rtype:
            tw, th = 1.2 * self.scale, 0.8 * self.scale
            if tw > w * 0.8: tw = w * 0.6
            tx, ty = cx - tw/2, cy - th/2
            dwg.add(dwg.rect((tx, ty), (tw, th), rx=2, ry=2, stroke=stroke, stroke_width=sw, fill="none"))
            dwg.add(dwg.circle((cx, ty-5), 5, stroke=stroke, fill="none"))
            dwg.add(dwg.circle((cx, ty+th+5), 5, stroke=stroke, fill="none"))

        elif "living" in rtype:
            sw, sh = 2.0 * self.scale, 0.8 * self.scale
            if sw > w * 0.9: sw = w * 0.8
            sx, sy = cx - sw/2, cy - sh/2
            dwg.add(dwg.rect((sx, sy), (sw, sh), rx=4, ry=4, stroke=stroke, stroke_width=sw, fill="none"))
            
        elif "bath" in rtype:
            # Toilet
            dwg.add(dwg.circle((cx, cy), 8, stroke=stroke, fill="none"))
            dwg.add(dwg.rect((cx-8, cy-18), (16, 10), stroke=stroke, fill="none"))

    def _draw_labels(self, dwg, room, off_x, off_y):
        geo = room["geometry"]
        x = geo["x"] * self.scale + off_x
        y = geo["y"] * self.scale + off_y
        w = geo["width"] * self.scale
        h = geo["height"] * self.scale
        cx, cy = x + w/2, y + h/2
        
        text_w, text_h = 120, 35
        dwg.add(dwg.rect((cx - text_w/2, cy - text_h/2 - 2), (text_w, text_h), 
                         fill="white", opacity=0.85, rx=4, ry=4))
        dwg.add(dwg.text(room["id"].replace("_", " ").upper(), 
                         insert=(cx, cy - 4), text_anchor="middle", 
                         font_family="Arial", font_weight="bold", font_size="13px", fill="black"))
        dim_str = f"{self._meters_to_feet(geo['width'])} x {self._meters_to_feet(geo['height'])}"
        dwg.add(dwg.text(dim_str, insert=(cx, cy + 12), text_anchor="middle", 
                         font_family="Consolas, monospace", font_size="11px", fill="#444"))

    def _draw_door_between(self, dwg, r1, r2, off_x, off_y):
        g1, g2 = r1["geometry"], r2["geometry"]
        overlap_y_start = max(g1["y"], g2["y"])
        overlap_y_end = min(g1["y"] + g1["height"], g2["y"] + g2["height"])
        overlap_x_start = max(g1["x"], g2["x"])
        overlap_x_end = min(g1["x"] + g1["width"], g2["x"] + g2["width"])
        
        door_size = 0.9 * self.scale
        
        if (overlap_y_end - overlap_y_start) > 0.5:
            mid_y = (overlap_y_start + overlap_y_end) / 2
            shared_x = g1["x"] if abs(g1["x"] - (g2["x"] + g2["width"])) < 0.1 else g2["x"]
            dx = shared_x * self.scale + off_x
            dy = mid_y * self.scale + off_y - door_size/2
            
            dwg.add(dwg.rect((dx - 2, dy), (4, door_size), fill="white"))
            dwg.add(dwg.path(d=f"M {dx},{dy} v {door_size}", stroke="black", stroke_width=1))
            dwg.add(dwg.path(d=f"M {dx},{dy} h {-door_size} A {door_size},{door_size} 0 0,1 {dx},{dy+door_size}", stroke="black", fill="none"))

        elif (overlap_x_end - overlap_x_start) > 0.5:
            mid_x = (overlap_x_start + overlap_x_end) / 2
            shared_y = g1["y"] if abs(g1["y"] - (g2["y"] + g2["height"])) < 0.1 else g2["y"]
            dx = mid_x * self.scale + off_x - door_size/2
            dy = shared_y * self.scale + off_y