#!/usr/bin/env python3
"""
GHOST-PROTOCOL: Main Entry Point
=================================
High-security, RAM-only encrypted vault application.

This is the main entry point that ties together:
- The GUI (CustomTkinter interface)
- Security monitors (Camera Sentinel, USB Guard)
- Cryptographic vault (AES-256 encryption in RAM)

CRITICAL: Data never touches the disk. It stays encrypted in RAM.
If a security trigger is tripped, RAM is overwritten with zeros and the app terminates.

Usage:
    python main.py [--bypass-usb] [--no-camera]
    
Options:
    --bypass-usb    Skip USB GHOST_KEY requirement (INSECURE - for development only)
    --no-camera     Disable camera monitoring
"""

import os
import sys
import time
import signal
import atexit
import argparse
import threading
from typing import Optional

# Cryptography
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Application modules
from gui import GhostProtocolGUI, Colors
from security_threads import CameraSentinel, USBGuard, get_system_info


class GhostProtocolVault:
    """
    The Vault: RAM-only encrypted storage.
    
    - Generates random AES-256 key on startup
    - Stores encrypted data only in memory
    - Provides secure memory wiping on exit
    """
    
    def __init__(self):
        """Initialize the vault with a random encryption key."""
        # Generate random AES-256 key (32 bytes = 256 bits)
        self._key = get_random_bytes(32)
        
        # Encrypted data storage (RAM only)
        self._encrypted_data: bytes = b""
        self._iv: bytes = b""
        
        # Flag to indicate if vault has been nuked
        self._nuked = False
        
        print("[VAULT] AES-256 encryption key generated")
        print("[VAULT] Memory-only vault initialized")
    
    def encrypt(self, plaintext: str) -> None:
        """
        Encrypt plaintext and store in RAM.
        
        Args:
            plaintext: The text to encrypt
        """
        if self._nuked:
            return
        
        try:
            # Generate random IV for each encryption
            self._iv = get_random_bytes(16)
            
            # Create cipher
            cipher = AES.new(self._key, AES.MODE_GCM, nonce=self._iv)
            
            # Encrypt data
            plaintext_bytes = plaintext.encode('utf-8')
            self._encrypted_data, _ = cipher.encrypt_and_digest(plaintext_bytes)
            
        except Exception as e:
            print(f"[VAULT ERROR] Encryption failed: {e}")
    
    def decrypt(self) -> str:
        """
        Decrypt and return stored data.
        
        Returns:
            The decrypted plaintext
        """
        if self._nuked or not self._encrypted_data:
            return ""
        
        try:
            # Create cipher with stored IV
            cipher = AES.new(self._key, AES.MODE_GCM, nonce=self._iv)
            
            # Decrypt data
            plaintext_bytes = cipher.decrypt(self._encrypted_data)
            return plaintext_bytes.decode('utf-8')
            
        except Exception as e:
            print(f"[VAULT ERROR] Decryption failed: {e}")
            return ""
    
    def nuke_memory(self) -> None:
        """
        Securely wipe all sensitive data from memory.
        
        This overwrites the encryption key, encrypted data, and IV
        with random bytes before setting them to empty values.
        """
        if self._nuked:
            return
        
        print("[VAULT] ████ INITIATING MEMORY WIPE ████")
        
        try:
            # Overwrite key with random data multiple times
            key_len = len(self._key) if self._key else 32
            for _ in range(3):
                self._key = os.urandom(key_len)
            self._key = b"\x00" * key_len
            
            # Overwrite encrypted data
            data_len = len(self._encrypted_data) if self._encrypted_data else 0
            if data_len > 0:
                for _ in range(3):
                    self._encrypted_data = os.urandom(data_len)
            self._encrypted_data = b""
            
            # Overwrite IV
            iv_len = len(self._iv) if self._iv else 16
            for _ in range(3):
                self._iv = os.urandom(iv_len)
            self._iv = b""
            
            self._nuked = True
            print("[VAULT] Memory wipe complete. All traces eliminated.")
            
        except Exception as e:
            print(f"[VAULT ERROR] Memory wipe error: {e}")
            # Force overwrite even on error
            self._key = b""
            self._encrypted_data = b""
            self._iv = b""
            self._nuked = True


class GhostProtocol:
    """
    Main GHOST-PROTOCOL application controller.
    
    Coordinates:
    - GUI interface
    - Security monitoring threads
    - Encrypted vault
    - Panic response
    """
    
    def __init__(self, bypass_usb: bool = False, enable_camera: bool = True):
        """
        Initialize GHOST-PROTOCOL.
        
        Args:
            bypass_usb: If True, bypass USB key requirement
            enable_camera: If True, enable camera monitoring
        """
        self.bypass_usb = bypass_usb
        self.enable_camera = enable_camera
        
        # Initialize components
        self.vault: Optional[GhostProtocolVault] = None
        self.gui: Optional[GhostProtocolGUI] = None
        self.camera_sentinel: Optional[CameraSentinel] = None
        self.usb_guard: Optional[USBGuard] = None
        
        # Panic state
        self._panic_triggered = False
        self._panic_lock = threading.Lock()
        
        # Register cleanup handlers
        atexit.register(self._cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals."""
        print(f"\n[SYSTEM] Received signal {signum}. Initiating secure shutdown...")
        self._trigger_panic()
    
    def _check_usb_key(self) -> bool:
        """
        Check if the GHOST_KEY USB is present.
        
        Returns:
            True if USB key is present or bypassed, False otherwise
        """
        if self.bypass_usb:
            print("[WARNING] USB key check BYPASSED - INSECURE MODE")
            return True
        
        print("[SYSTEM] Scanning for GHOST_KEY USB device...")
        
        if USBGuard.check_ghost_key_present():
            print("[SYSTEM] GHOST_KEY detected. Access granted.")
            return True
        
        print("")
        print("=" * 60)
        print("[DENIED] GHOST_KEY USB NOT DETECTED")
        print("")
        print("  To launch GHOST-PROTOCOL, you must:")
        print("  1. Insert a USB drive labeled 'GHOST_KEY'")
        print("  2. Restart this application")
        print("")
        print("  For development/testing, use: --bypass-usb")
        print("=" * 60)
        print("")
        return False
    
    def _trigger_panic(self) -> None:
        """
        Execute panic protocol - wipe memory and terminate.
        
        This is called when:
        - Multiple faces detected (shoulder surfer)
        - USB key removed
        - Manual panic button pressed
        - Termination signal received
        """
        with self._panic_lock:
            if self._panic_triggered:
                return
            self._panic_triggered = True
        
        print("")
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║   ███████╗██████╗  ██████╗ ████████╗ ██████╗  ██████╗    ║")
        print("║   ██╔══██║██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝    ║")
        print("║   ██████╔╝██████╔╝██║   ██║   ██║   ██║   ██║██║         ║")
        print("║   ██╔═══╝ ██╔══██╗██║   ██║   ██║   ██║   ██║██║         ║")
        print("║   ██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝╚██████╗    ║")
        print("║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝    ║")
        print("║" + " " * 58 + "║")
        print("║" + "═" * 58 + "║")
        print("║   [CRITICAL] EXECUTING PROTOCOL ZERO                      ║")
        print("║   [CRITICAL] WIPING ALL MEMORY                            ║")
        print("║   [CRITICAL] TERMINATING PROCESS                          ║")
        print("╚" + "═" * 58 + "╝")
        print("")
        
        # Stop security monitors
        self._stop_monitors()
        
        # Wipe the vault
        if self.vault:
            self.vault.nuke_memory()
        
        # Clear GUI if possible
        if self.gui:
            try:
                self.gui.show_wipe_animation()
                self.gui.clear_secrets()
            except Exception:
                pass
        
        print("[SYSTEM] Secure shutdown complete. Goodbye.")
        
        # Force terminate
        os._exit(0)
    
    def _update_status(self, key: str, value: str) -> None:
        """Thread-safe status update for GUI."""
        if self.gui:
            try:
                self.gui.update_status(key, value)
            except Exception:
                pass
    
    def _set_blur(self, blur: bool) -> None:
        """Thread-safe blur control for GUI."""
        if self.gui:
            try:
                self.gui.set_blur(blur)
            except Exception:
                pass
    
    def _start_monitors(self) -> None:
        """Start security monitoring threads."""
        # Camera Sentinel
        if self.enable_camera:
            self.camera_sentinel = CameraSentinel(
                panic_callback=self._trigger_panic,
                status_callback=self._update_status,
                blur_callback=self._set_blur
            )
            self.camera_sentinel.start()
            print("[SYSTEM] Camera Sentinel ACTIVE")
        else:
            print("[WARNING] Camera Sentinel DISABLED")
            self._update_status("camera", "DISABLED")
        
        # USB Guard
        self.usb_guard = USBGuard(
            panic_callback=self._trigger_panic,
            status_callback=self._update_status
        )
        if self.bypass_usb:
            self.usb_guard.set_bypass_mode(True)
        self.usb_guard.start()
        print("[SYSTEM] USB Guard ACTIVE")
        
        # Set initial threat level
        self._update_status("threat", "LOW")
    
    def _stop_monitors(self) -> None:
        """Stop all security monitoring threads."""
        if self.camera_sentinel:
            self.camera_sentinel.stop()
        if self.usb_guard:
            self.usb_guard.stop()
    
    def _cleanup(self) -> None:
        """Cleanup handler called on exit."""
        if not self._panic_triggered:
            self._trigger_panic()
    
    def run(self) -> int:
        """
        Run the GHOST-PROTOCOL application.
        
        Returns:
            Exit code (0 = success, 1 = error)
        """
        # Print system info
        print("[SYSTEM] Gathering system information...")
        sys_info = get_system_info()
        print(f"[SYSTEM] Platform: {sys_info['platform']} {sys_info['platform_release']}")
        print(f"[SYSTEM] Python: {sys_info['python_version']}")
        
        # Check for USB key
        if not self._check_usb_key():
            return 1
        
        # Initialize vault
        print("[SYSTEM] Initializing encrypted vault...")
        self.vault = GhostProtocolVault()
        
        # Create GUI
        print("[SYSTEM] Building interface...")
        self.gui = GhostProtocolGUI(
            panic_callback=self._trigger_panic,
            bypass_usb=self.bypass_usb
        )
        
        # Start security monitors
        print("[SYSTEM] Activating security protocols...")
        self._start_monitors()
        
        print("")
        print("[SYSTEM] ████ GHOST-PROTOCOL ACTIVE ████")
        print("[SYSTEM] All systems operational. Vault is ready.")
        print("")
        
        # Run the GUI main loop
        try:
            self.gui.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            if not self._panic_triggered:
                self._trigger_panic()
        
        return 0


def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="GHOST-PROTOCOL: RAM-only encrypted vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                  # Normal operation (requires GHOST_KEY USB)
  python main.py --bypass-usb     # Development mode (no USB required)
  python main.py --no-camera      # Disable camera monitoring
        """
    )
    
    parser.add_argument(
        "--bypass-usb",
        action="store_true",
        help="Bypass USB key requirement (INSECURE - for development only)"
    )
    
    parser.add_argument(
        "--no-camera",
        action="store_true",
        help="Disable camera monitoring"
    )
    
    args = parser.parse_args()
    
    # Security warnings
    if args.bypass_usb:
        print("")
        print("╔" + "═" * 58 + "╗")
        print("║  ⚠ WARNING: USB KEY BYPASS ENABLED                        ║")
        print("║  This mode is INSECURE and for development only!          ║")
        print("╚" + "═" * 58 + "╝")
        print("")
    
    # Create and run the application
    app = GhostProtocol(
        bypass_usb=args.bypass_usb,
        enable_camera=not args.no_camera
    )
    
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
