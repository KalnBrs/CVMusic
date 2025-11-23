import math

def verify_chord_placement(target_positions, detected_fingertips, threshold=40.0):
    """
    Verify if detected fingertips match the target note positions.
    
    Args:
        target_positions (list): List of dicts {'x': int, 'y': int} or None.
        detected_fingertips (list): List of tuples (x, y).
        threshold (float): Max distance in pixels to consider a "hit".
        
    Returns:
        list: List of booleans or None, matching the input target_positions structure.
              True if a finger is close enough, False otherwise, None if no target.
    """
    results = []
    
    for target in target_positions:
        if target is None:
            results.append(None)
            continue
            
        target_x = target['x']
        target_y = target['y']
        
        is_correct = False
        # Check if ANY fingertip is within range of this target
        for (fx, fy) in detected_fingertips:
            dist = math.sqrt((target_x - fx)**2 + (target_y - fy)**2)
            if dist <= threshold:
                is_correct = True
                break
        
        results.append(is_correct)
        
    return results

