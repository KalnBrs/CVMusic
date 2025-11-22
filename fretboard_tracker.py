import cv2
import numpy as np
import json
import os
from typing import Tuple, List, Optional, Dict, Any

class FretboardTracker:
    """
    Tracks the guitar fretboard plane using SIFT feature matching.
    Allows projecting a static 'reference grid' onto dynamic frames.
    """
    
    def __init__(self, reference_image_path: str, min_match_count: int = 10):
        self.min_match_count = min_match_count
        
        # Load Reference Image
        self.ref_img = cv2.imread(reference_image_path)
        if self.ref_img is None:
            raise ValueError(f"Could not load reference image: {reference_image_path}")
            
        # Resize ref image for performance (optional, but good for SIFT speed)
        # Keeping original size for precision, but SIFT might be slow on 4K.
        # Assuming images are reasonable (< 2000px wide).
        
        self.ref_gray = cv2.cvtColor(self.ref_img, cv2.COLOR_BGR2GRAY)
        
        # Initialize Detector (SIFT is robust to scale/rotation)
        self.sift = cv2.SIFT_create()
        
        # Compute Reference Keypoints & Descriptors ONCE
        self.kp_ref, self.des_ref = self.sift.detectAndCompute(self.ref_gray, None)
        print(f"✅ FretboardTracker initialized. Reference keypoints: {len(self.kp_ref)}")
        
        # Initialize Matcher (FLANN based is faster than BF)
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
        
        # Store last valid homography for smoothing (optional)
        self.last_H = None

    def process_frame(self, frame_bgr: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Detects the fretboard in the current frame.
        
        :param frame_bgr: Current video frame
        :return: (Homography Matrix (3x3), Mask of matches)
                 Returns (None, None) if tracking fails.
        """
        frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        
        # Detect keypoints in current frame
        kp_frame, des_frame = self.sift.detectAndCompute(frame_gray, None)
        
        if des_frame is None or len(kp_frame) < self.min_match_count:
            return None, None
            
        # Match descriptors
        matches = self.matcher.knnMatch(self.des_ref, des_frame, k=2)
        
        # Filter matches using Lowe's ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)
                
        if len(good_matches) >= self.min_match_count:
            # Extract location of good matches
            src_pts = np.float32([self.kp_ref[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # Find Homography
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            
            if M is not None:
                self.last_H = M
                return M, mask
        
        return None, None

    def map_point_to_reference(self, x: float, y: float, H: np.ndarray) -> Optional[Tuple[float, float]]:
        """
        Maps a point from the Current Frame BACK to the Reference Image coordinates.
        Used to check where a fingertip (in frame) lands on the Reference Grid.
        """
        try:
            H_inv = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            return None
            
        # Transform point
        pt_original = np.array([[[x, y]]], dtype=np.float32)
        pt_transformed = cv2.perspectiveTransform(pt_original, H_inv)
        
        return pt_transformed[0][0][0], pt_transformed[0][0][1]

class GridSystem:
    """
    Manages the 'Perfect Grid' defined on the Reference Image.
    Can save/load from JSON.
    """
    def __init__(self):
        self.strings = {} # { "1": [(x1,y1), (x2,y2)], ... }
        self.frets = []   # [x_fret0, x_fret1, ...] (assuming vertical lines for now, or generalized lines)
        self.fret_lines = [] # List of [(x1,y1), (x2,y2)] for generalized frets
        
    def load_from_json(self, json_path: str):
        if not os.path.exists(json_path):
            print(f"⚠️ Grid JSON not found: {json_path}")
            return
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        # Load strings
        raw_strings = data.get("strings", {})
        for k, v in raw_strings.items():
            self.strings[k] = v # Expects list of 2 points
            
        # Load frets (generalized lines)
        self.fret_lines = data.get("fret_lines", [])
        
    def save_to_json(self, json_path: str):
        data = {
            "strings": self.strings,
            "fret_lines": self.fret_lines
        }
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_fret_index(self, x_ref: float, y_ref: float) -> int:
        """
        Determines fret index for a point in Reference Coordinates.
        This is a simplified implementation assuming frets are roughly vertical
        and sorted from Nut (left or right) to Bridge.
        
        You should perform a geometric check: which two fret lines is the point between?
        """
        # TODO: Implement robust point-in-polygon or between-lines check
        # For now, let's assume we have x-coordinates of frets sorted
        if not self.fret_lines:
            return -1
            
        # Simplified: just check X against average X of fret lines
        # (Only works if reference image is horizontal)
        pt_x = x_ref
        
        fret_xs = []
        for line in self.fret_lines:
            x_avg = (line[0][0] + line[1][0]) / 2
            fret_xs.append(x_avg)
            
        # Auto-detect direction: 
        # If fret_xs[1] - fret_xs[0] > fret_xs[2] - fret_xs[1], it's getting smaller => Nut is at index 0
        # Actually, let's just assume the JSON is sorted 0..N
        
        # We need to handle the "Nut on Right" case based on the sorted values
        is_reversed = fret_xs[-1] < fret_xs[0]
        
        if is_reversed:
            # Nut is on Right (High X)
            if pt_x > fret_xs[0]: return 0 # Open
            for i in range(len(fret_xs)-1):
                if fret_xs[i+1] <= pt_x < fret_xs[i]:
                    return i + 1
        else:
            # Nut is on Left (Low X)
            if pt_x < fret_xs[0]: return 0 # Open
            for i in range(len(fret_xs)-1):
                if fret_xs[i] <= pt_x < fret_xs[i+1]:
                    return i + 1
                    
        return len(fret_xs) # High fret

    def get_string_index(self, x_ref: float, y_ref: float) -> int:
        """
        Determines string index (1..6).
        Checks which string lines the point is closest to, or between.
        """
        # Simple closest line check
        best_dist = float('inf')
        best_idx = -1
        
        for name, pts in self.strings.items():
            p1, p2 = np.array(pts[0]), np.array(pts[1])
            p = np.array([x_ref, y_ref])
            
            # Distance from point to line segment
            # (Simplified to infinite line for speed)
            d = np.linalg.norm(np.cross(p2-p1, p1-p)) / np.linalg.norm(p2-p1)
            
            if d < best_dist:
                best_dist = d
                best_idx = int(name)
        
        # Check if distance is reasonable (e.g. within neck width)
        if best_dist > 50: # pixels tolerance
            return None
            
        return best_idx

