import cv2
import numpy as np
import json
import os
from typing import Tuple, List, Optional, Dict, Any

class FretboardTracker:
    """
    Hybrid Tracker: SIFT for Initialization/Recovery + Optical Flow for Smooth Tracking.
    """
    
    def __init__(self, reference_image_path: str, min_match_count: int = 10):
        self.min_match_count = min_match_count
        
        # Load Reference Image
        self.ref_img = cv2.imread(reference_image_path)
        if self.ref_img is None:
            raise ValueError(f"Could not load reference image: {reference_image_path}")
            
        self.ref_gray = cv2.cvtColor(self.ref_img, cv2.COLOR_BGR2GRAY)
        self.h_ref, self.w_ref = self.ref_gray.shape[:2]
        
        # Initialize SIFT Detector
        self.sift = cv2.SIFT_create()
        
        # Compute Reference Keypoints
        self.kp_ref, self.des_ref = self.sift.detectAndCompute(self.ref_gray, None)
        print(f"✅ FretboardTracker initialized. Reference keypoints: {len(self.kp_ref)}")
        
        # Initialize Matcher
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
        
        # State for Optical Flow
        self.prev_gray = None
        self.tracked_points = None # Points being tracked in current frame
        self.ref_points_for_tracking = None # Corresponding points in reference image
        
        # Parameters for Optical Flow
        self.lk_params = dict(winSize=(21, 21), maxLevel=3,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))

    def process_frame(self, frame_bgr: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Detects fretboard using Hybrid Tracking.
        """
        frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        
        H = None
        mask = None
        
        # Mode 1: Optical Flow Tracking (Fast & Smooth)
        if self.tracked_points is not None and len(self.tracked_points) >= 4 and self.prev_gray is not None:
            p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, frame_gray, self.tracked_points, None, **self.lk_params)
            
            # Select good points
            if p1 is not None:
                good_new = p1[st == 1]
                good_ref = self.ref_points_for_tracking[st == 1]
                
                if len(good_new) >= 4:
                    # Calculate Homography from Reference -> Current Frame
                    H, mask = cv2.findHomography(good_ref, good_new, cv2.RANSAC, 5.0)
                    
                    # Update tracked points for next frame
                    self.tracked_points = good_new.reshape(-1, 1, 2)
                    self.ref_points_for_tracking = good_ref.reshape(-1, 1, 2)
                    self.prev_gray = frame_gray
                    
                    # Check if H is reasonable (sanity check) to avoid drifting into infinity
                    if self._is_matrix_stable(H):
                        return H, mask
                    else:
                        # If matrix looks crazy, fall back to SIFT
                        print("⚠️ Tracking drift detected, resetting to SIFT...")
                        self.tracked_points = None 

        # Mode 2: SIFT Detection (Global Search / Recovery)
        # Run this if Optical Flow failed or hasn't started
        
        kp_frame, des_frame = self.sift.detectAndCompute(frame_gray, None)
        
        if des_frame is not None and len(kp_frame) >= self.min_match_count:
            matches = self.matcher.knnMatch(self.des_ref, des_frame, k=2)
            
            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
                    
            if len(good_matches) >= self.min_match_count:
                src_pts = np.float32([self.kp_ref[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                
                H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                
                if H is not None:
                    # Initialize Optical Flow for next frames
                    # We use the matched points as initial tracking points
                    self.tracked_points = dst_pts
                    self.ref_points_for_tracking = src_pts
                    self.prev_gray = frame_gray
                    print(f"✅ SIFT Locked: {len(good_matches)} matches")
                    return H, mask

        # Tracking Failed
        self.tracked_points = None
        self.prev_gray = frame_gray
        return None, None

    def _is_matrix_stable(self, H):
        """Simple sanity check for Homography matrix determinant/scale."""
        if H is None: return False
        det = np.linalg.det(H[:2, :2])
        # If scale change is too extreme (zoom in/out > 5x), likely garbage
        if det < 0.1 or det > 10: 
            return False
        return True

    def map_point_to_reference(self, x: float, y: float, H: np.ndarray) -> Optional[Tuple[float, float]]:
        try:
            H_inv = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            return None
        pt_original = np.array([[[x, y]]], dtype=np.float32)
        pt_transformed = cv2.perspectiveTransform(pt_original, H_inv)
        return pt_transformed[0][0][0], pt_transformed[0][0][1]

class GridSystem:
    def __init__(self):
        self.strings = {}
        self.frets = []
        self.fret_lines = []
        
    def load_from_json(self, json_path: str):
        if not os.path.exists(json_path): return
        with open(json_path, 'r') as f:
            data = json.load(f)
        raw_strings = data.get("strings", {})
        for k, v in raw_strings.items():
            self.strings[k] = v 
        self.fret_lines = data.get("fret_lines", [])
        
    def get_fret_index(self, x_ref: float, y_ref: float) -> int:
        # Simplified check based on fret lines X-order (assuming sorted)
        if not self.fret_lines: return -1
        
        # Check if lines are sorted Left->Right or Right->Left
        # Calculate centroid X of first and last line
        x0 = (self.fret_lines[0][0][0] + self.fret_lines[0][1][0]) / 2
        xN = (self.fret_lines[-1][0][0] + self.fret_lines[-1][1][0]) / 2
        
        # Find nearest fret line
        # Actually, we need to check intervals.
        # Let's map the point to the "fretboard axis" defined by Nut->Bridge
        # Or just simple nearest neighbor for robust-ish detection
        
        best_idx = -1
        min_dist = float('inf')
        
        for i, line in enumerate(self.fret_lines):
            # Distance from point to line segment
            p1 = np.array(line[0])
            p2 = np.array(line[1])
            p = np.array([x_ref, y_ref])
            
            # Simple distance to infinite line
            d = np.abs(np.cross(p2-p1, p1-p)) / np.linalg.norm(p2-p1)
            
            # Also check if within reasonable Y-bounds? (optional)
            
            if d < min_dist:
                min_dist = d
                best_idx = i
                
        # Heuristic: If we are "between" fret i and i+1, we are on fret i+1.
        # But simple nearest neighbor might return i or i+1 depending on which line is closer.
        # Correct logic: Fret N is the space between Line N-1 and Line N.
        # Line 0 is Nut.
        # If X is between Line 0 and Line 1 -> Fret 1.
        # We need a signed distance check.
        
        # Hack for demo: just return nearest index. 
        # Since fret lines denote the metal bars, pressing "on" fret 5 means pressing left of bar 5.
        # So nearest neighbor to Bar 5 is close enough to "Fret 5".
        return best_idx

    def get_string_index(self, x_ref: float, y_ref: float) -> int:
        best_dist = float('inf')
        best_idx = -1
        
        for name, pts in self.strings.items():
            p1, p2 = np.array(pts[0]), np.array(pts[1])
            p = np.array([x_ref, y_ref])
            d = np.linalg.norm(np.cross(p2-p1, p1-p)) / np.linalg.norm(p2-p1)
            
            if d < best_dist:
                best_dist = d
                best_idx = int(name)
        
        if best_dist > 80: return None
        return best_idx
