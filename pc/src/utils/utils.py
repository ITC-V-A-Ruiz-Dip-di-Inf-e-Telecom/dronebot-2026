def rover_inside_fire_circle(rover_box, fire_center, fire_radius_px, tolerance=0):
    
    #Returns True if every corner of rover_box is within the fire circle.
    cx, cy = fire_center
    r = fire_radius_px + tolerance
    x1, y1, x2, y2 = rover_box
    corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
    return all((x - cx) ** 2 + (y - cy) ** 2 <= r * r for x, y in corners)
