"""
GHOST-PROTOCOL: Security Threads Module
========================================
Contains the camera sentinel (face detection) and USB guard logic.
All security monitoring runs in background threads.
"""

import os
import sys
import time
import threading
import platform
from typing import Callable, Optional

import cv2
import psutil


class SecurityMonitor:
    """Base class for security monitoring threads."""
    
    def __init__(self, panic_callback: Callable[[], None], status_callback: Callable[[str, str], None]):
        """
        Initialize the security monitor.
        
        Args:
            panic_callback: Function to call when panic is triggered
            status_callback: Function to call to update status (key, value)
        """
        self.panic_callback = panic_callback
        self.status_callback = status_callback
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start the monitoring thread."""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the monitoring thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
    
    def _monitor_loop(self) -> None:
        """Override in subclass to implement monitoring logic."""
        raise NotImplementedError


class CameraSentinel(SecurityMonitor):
    """
    The Sentinel: OpenCV Face Detection Monitor
    
    - 0 Faces visible (User left desk) -> Blur window & Lock
    - > 1 Face visible (Shoulder Surfer detected) -> TRIGGER PANIC WIPE
    """
    
    FRAME_INTERVAL = 0.5  # Process 1 frame every 0.5 seconds
    
    def __init__(self, panic_callback: Callable[[], None], 
                 status_callback: Callable[[str, str], None],
                 blur_callback: Callable[[bool], None]):
        """
        Initialize the camera sentinel.
        
        Args:
            panic_callback: Function to call when multiple faces detected
            status_callback: Function to call to update camera status
            blur_callback: Function to call to blur/unblur the window
        """
        super().__init__(panic_callback, status_callback)
        self.blur_callback = blur_callback
        self.cap: Optional[cv2.VideoCapture] = None
        self.face_cascade: Optional[cv2.CascadeClassifier] = None
        self._camera_available = False
    
    def _initialize_camera(self) -> bool:
        """Initialize camera and face detection cascade."""
        try:
            # Load the Haar cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                print("[WARNING] Failed to load face cascade classifier")
                return False
            
            # Try to open the camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("[WARNING] Camera not available. Sentinel in STANDBY mode.")
                self.status_callback("camera", "NO CAMERA")
                return False
            
            self._camera_available = True
            self.status_callback("camera", "ARMED")
            print("[SYSTEM] SENTINEL ACTIVATED. Camera monitoring initiated.")
            return True
            
        except Exception as e:
            print(f"[ERROR] Camera initialization failed: {e}")
            self.status_callback("camera", "ERROR")
            return False
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop for face detection."""
        if not self._initialize_camera():
            # Camera not available, run in degraded mode
            while self._running:
                time.sleep(1.0)
            return
        
        last_face_count = 1  # Assume user is present initially
        
        while self._running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(self.FRAME_INTERVAL)
                    continue
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                face_count = len(faces)
                
                if face_count == 0:
                    # User left desk - blur and lock
                    if last_face_count != 0:
                        print("[ALERT] USER ABSENT. Engaging privacy shield.")
                        self.status_callback("camera", "LOCKED")
                        self.blur_callback(True)
                
                elif face_count == 1:
                    # Normal operation - single authorized user
                    if last_face_count != 1:
                        print("[SYSTEM] User presence confirmed. Disengaging privacy shield.")
                        self.status_callback("camera", "ARMED")
                        self.blur_callback(False)
                
                else:
                    # INTRUDER DETECTED - PANIC WIPE
                    print("")
                    print("=" * 60)
                    print("[CRITICAL] ████ INTRUDER DETECTED ████")
                    print("[CRITICAL] MULTIPLE FACES DETECTED. SHOULDER SURFER ALERT!")
                    print("[CRITICAL] INITIATING PROTOCOL 0.")
                    print("=" * 60)
                    print("")
                    self.status_callback("camera", "BREACH")
                    self.status_callback("threat", "CRITICAL")
                    self.panic_callback()
                    break
                
                last_face_count = face_count
                
            except Exception as e:
                print(f"[ERROR] Camera processing error: {e}")
            
            time.sleep(self.FRAME_INTERVAL)
        
        # Cleanup
        if self.cap is not None:
            self.cap.release()
    
    def stop(self) -> None:
        """Stop the camera monitoring and release resources."""
        super().stop()
        if self.cap is not None:
            self.cap.release()


class USBGuard(SecurityMonitor):
    """
    The Dead Man's Key: USB Guard
    
    - App starts ONLY if USB drive named 'GHOST_KEY' is detected
    - If USB is removed while app is running -> IMMEDIATELY WIPE RAM and kill process
    """
    
    CHECK_INTERVAL = 0.5  # Check USB status every 0.5 seconds
    REQUIRED_USB_NAME = "GHOST_KEY"
    
    def __init__(self, panic_callback: Callable[[], None], 
                 status_callback: Callable[[str, str], None]):
        super().__init__(panic_callback, status_callback)
        self._usb_present = False
        self._bypass_mode = False
        self._bypass_lock = threading.Lock()
    
    @classmethod
    def check_ghost_key_present(cls) -> bool:
        """
        Check if the GHOST_KEY USB is currently mounted.
        
        Returns:
            True if GHOST_KEY is present, False otherwise
        """
        try:
            partitions = psutil.disk_partitions(all=True)
            
            for partition in partitions:
                # Check the mount point or device name for GHOST_KEY
                mount_point = partition.mountpoint
                device = partition.device
                
                if platform.system() == "Windows":
                    # On Windows, check volume label
                    try:
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        volume_name = ctypes.create_unicode_buffer(1024)
                        kernel32.GetVolumeInformationW(
                            mount_point + "\\",
                            volume_name, 1024,
                            None, None, None, None, 0
                        )
                        if volume_name.value == cls.REQUIRED_USB_NAME:
                            return True
                    except Exception:
                        pass
                else:
                    # On Linux/Mac, check if GHOST_KEY is in mount path
                    if cls.REQUIRED_USB_NAME in mount_point:
                        return True
                    
                    # Also check /dev/disk/by-label on Linux
                    label_path = f"/dev/disk/by-label/{cls.REQUIRED_USB_NAME}"
                    if os.path.exists(label_path):
                        return True
                    
                    # Check /media and /mnt directories for GHOST_KEY
                    for base_dir in ["/media", "/mnt", "/run/media"]:
                        if os.path.exists(base_dir):
                            try:
                                for user_dir in os.listdir(base_dir):
                                    key_path = os.path.join(base_dir, user_dir, cls.REQUIRED_USB_NAME)
                                    if os.path.exists(key_path) and os.path.isdir(key_path):
                                        return True
                                    # Also check direct mount
                                    if user_dir == cls.REQUIRED_USB_NAME:
                                        return True
                            except PermissionError:
                                # Skip directories we don't have permission to read
                                continue
            
            return False
            
        except Exception as e:
            print(f"[ERROR] USB check failed: {e}")
            return False
    
    def set_bypass_mode(self, bypass: bool) -> None:
        """
        Enable or disable bypass mode (for development/testing).
        
        Args:
            bypass: If True, USB requirement is bypassed
        
        Note: This should be called before starting the monitor thread.
        """
        with self._bypass_lock:
            self._bypass_mode = bypass
        if bypass:
            print("[WARNING] USB Guard BYPASS MODE enabled - INSECURE")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop for USB presence."""
        with self._bypass_lock:
            bypass_mode = self._bypass_mode
        
        if bypass_mode:
            self.status_callback("usb", "BYPASSED")
            print("[WARNING] USB Guard running in BYPASS mode")
            while self._running:
                time.sleep(self.CHECK_INTERVAL)
            return
        
        # Initial check
        self._usb_present = self.check_ghost_key_present()
        
        if self._usb_present:
            self.status_callback("usb", "SECURE")
            print("[SYSTEM] GHOST_KEY detected. USB Guard ACTIVE.")
        else:
            self.status_callback("usb", "NO KEY")
            print("[WARNING] GHOST_KEY not detected. Operating in limited mode.")
        
        initial_state = self._usb_present
        
        while self._running:
            current_state = self.check_ghost_key_present()
            
            if initial_state and not current_state:
                # USB was present at start but now removed - PANIC
                print("")
                print("=" * 60)
                print("[CRITICAL] ████ DEAD MAN'S KEY REMOVED ████")
                print("[CRITICAL] GHOST_KEY USB DISCONNECTED!")
                print("[CRITICAL] INITIATING PROTOCOL 0.")
                print("=" * 60)
                print("")
                self.status_callback("usb", "REMOVED")
                self.status_callback("threat", "CRITICAL")
                self.panic_callback()
                break
            
            if current_state and not self._usb_present:
                # USB reconnected
                self.status_callback("usb", "SECURE")
                print("[SYSTEM] GHOST_KEY reconnected. Security restored.")
            elif not current_state and self._usb_present:
                # USB disconnected (but was not present at start)
                self.status_callback("usb", "NO KEY")
            
            self._usb_present = current_state
            time.sleep(self.CHECK_INTERVAL)


def get_system_info() -> dict:
    """Get system information for security logging."""
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }
