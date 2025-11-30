"""
GHOST-PROTOCOL: GUI Module
===========================
CustomTkinter-based high-DPI interface with "Stealth Mode" theme.
Dark black background, neon green text - cinematic CIA/NSA terminal aesthetic.
"""

import os
import sys
import threading
from typing import Callable, Optional

import customtkinter as ctk


# Theme Colors - Stealth Mode
class Colors:
    """Stealth Mode color palette."""
    BACKGROUND = "#0a0a0a"          # Deep black
    BACKGROUND_DARK = "#050505"     # Darker black for panels
    PANEL_BG = "#0d0d0d"            # Panel background
    NEON_GREEN = "#00ff41"          # Primary neon green
    NEON_GREEN_DIM = "#00aa2a"      # Dimmed green
    NEON_GREEN_DARK = "#005511"     # Dark green for borders
    WARNING_YELLOW = "#ffcc00"      # Warning status
    DANGER_RED = "#ff0040"          # Danger/Panic
    SECURE_BLUE = "#00d4ff"         # Secure status
    TEXT_PRIMARY = "#00ff41"        # Primary text (green)
    TEXT_SECONDARY = "#008822"      # Secondary text (darker green)
    BORDER = "#00ff41"              # Border color


class StatusPanel(ctk.CTkFrame):
    """Security status panel showing camera, USB, and threat level."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(
            fg_color=Colors.PANEL_BG,
            corner_radius=0,
            border_width=1,
            border_color=Colors.NEON_GREEN_DARK
        )
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="▓▓▓ STATUS PANEL ▓▓▓",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=Colors.NEON_GREEN
        )
        self.title_label.pack(pady=(15, 20), padx=10)
        
        # Separator line
        self.separator1 = ctk.CTkFrame(self, height=1, fg_color=Colors.NEON_GREEN_DARK)
        self.separator1.pack(fill="x", padx=10, pady=5)
        
        # Camera Status
        self.camera_frame = self._create_status_row("CAMERA:", "INITIALIZING")
        self.camera_frame.pack(fill="x", padx=10, pady=10)
        
        # USB Status
        self.usb_frame = self._create_status_row("USB KEY:", "SCANNING")
        self.usb_frame.pack(fill="x", padx=10, pady=10)
        
        # Separator line
        self.separator2 = ctk.CTkFrame(self, height=1, fg_color=Colors.NEON_GREEN_DARK)
        self.separator2.pack(fill="x", padx=10, pady=10)
        
        # Threat Level
        self.threat_frame = self._create_status_row("THREAT:", "LOW")
        self.threat_frame.pack(fill="x", padx=10, pady=10)
        
        # Status indicators dictionary for easy updates
        self._status_labels = {}
    
    def _create_status_row(self, label_text: str, value_text: str) -> ctk.CTkFrame:
        """Create a status row with label and value."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        
        label = ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            width=80
        )
        label.pack(side="left", padx=(5, 10))
        
        value = ctk.CTkLabel(
            frame,
            text=f"[{value_text}]",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=Colors.NEON_GREEN,
            anchor="w"
        )
        value.pack(side="left", fill="x", expand=True)
        
        # Store reference to value label
        key = label_text.replace(":", "").lower().replace(" ", "_")
        self._status_labels[key] = value
        
        return frame
    
    def update_status(self, key: str, value: str) -> None:
        """Update a status indicator."""
        # Map keys to label references
        key_map = {
            "camera": "camera",
            "usb": "usb_key",
            "threat": "threat"
        }
        
        label_key = key_map.get(key, key)
        
        if label_key in self._status_labels:
            label = self._status_labels[label_key]
            label.configure(text=f"[{value}]")
            
            # Set color based on status
            if value in ["ARMED", "SECURE", "LOW"]:
                label.configure(text_color=Colors.NEON_GREEN)
            elif value in ["LOCKED", "NO KEY", "MEDIUM", "NO CAMERA", "BYPASSED"]:
                label.configure(text_color=Colors.WARNING_YELLOW)
            elif value in ["BREACH", "REMOVED", "CRITICAL", "HIGH", "ERROR"]:
                label.configure(text_color=Colors.DANGER_RED)
            else:
                label.configure(text_color=Colors.NEON_GREEN)


class SecretTextArea(ctk.CTkFrame):
    """Encrypted text area for storing secrets."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(
            fg_color=Colors.BACKGROUND_DARK,
            corner_radius=0,
            border_width=2,
            border_color=Colors.NEON_GREEN_DARK
        )
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color=Colors.PANEL_BG, corner_radius=0)
        self.header_frame.pack(fill="x")
        
        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="█▀▀ CLASSIFIED NOTES █▀▀",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color=Colors.NEON_GREEN
        )
        self.header_label.pack(pady=10)
        
        # Text area
        self.textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=14),
            fg_color=Colors.BACKGROUND,
            text_color=Colors.NEON_GREEN,
            border_width=0,
            corner_radius=0,
            wrap="word"
        )
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Placeholder text
        self._set_placeholder()
    
    def _set_placeholder(self) -> None:
        """Set placeholder text in the text area."""
        placeholder = """
╔══════════════════════════════════════════════════════════════════╗
║                     GHOST-PROTOCOL VAULT                         ║
║━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━║
║                                                                  ║
║  ► All data is encrypted in RAM only                            ║
║  ► Nothing is written to disk                                   ║
║  ► Security monitors are active                                 ║
║                                                                  ║
║  Type your classified notes below...                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

"""
        self.textbox.insert("1.0", placeholder)
    
    def get_text(self) -> str:
        """Get the current text content."""
        return self.textbox.get("1.0", "end-1c")
    
    def clear(self) -> None:
        """Clear the text area."""
        self.textbox.delete("1.0", "end")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the text area."""
        state = "normal" if enabled else "disabled"
        self.textbox.configure(state=state)


class BlurOverlay(ctk.CTkFrame):
    """Privacy blur overlay shown when user is not present."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(
            fg_color=Colors.BACKGROUND,
            corner_radius=0
        )
        
        # Center container
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Lock icon (ASCII art style)
        self.lock_label = ctk.CTkLabel(
            self.center_frame,
            text="""
    ████████████████
    ██            ██
    ██    ████    ██
    ██    ████    ██
    ██            ██
████████████████████████
██                    ██
██    ██████████      ██
██    ██      ██      ██
██    ██████████      ██
██                    ██
████████████████████████
""",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=Colors.NEON_GREEN_DIM
        )
        self.lock_label.pack()
        
        # Lock message
        self.message_label = ctk.CTkLabel(
            self.center_frame,
            text="PRIVACY SHIELD ENGAGED",
            font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
            text_color=Colors.WARNING_YELLOW
        )
        self.message_label.pack(pady=20)
        
        # Instruction
        self.instruction_label = ctk.CTkLabel(
            self.center_frame,
            text="Return to terminal to restore access",
            font=ctk.CTkFont(family="Consolas", size=14),
            text_color=Colors.TEXT_SECONDARY
        )
        self.instruction_label.pack()
        
        # Hide by default
        self.place_forget()
    
    def show(self) -> None:
        """Show the blur overlay."""
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
    
    def hide(self) -> None:
        """Hide the blur overlay."""
        self.place_forget()


class GhostProtocolGUI(ctk.CTk):
    """Main GHOST-PROTOCOL GUI application."""
    
    def __init__(self, 
                 panic_callback: Optional[Callable[[], None]] = None,
                 bypass_usb: bool = False):
        """
        Initialize the GHOST-PROTOCOL GUI.
        
        Args:
            panic_callback: Function to call when panic is triggered
            bypass_usb: If True, bypass USB key requirement
        """
        super().__init__()
        
        self.panic_callback = panic_callback
        self.bypass_usb = bypass_usb
        self._is_locked = False
        
        # Configure window
        self.title("GHOST-PROTOCOL v1.0 // CLASSIFIED")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Configure colors
        self.configure(fg_color=Colors.BACKGROUND)
        
        # Build the interface
        self._build_header()
        self._build_main_content()
        self._build_footer()
        self._build_blur_overlay()
        
        # Print startup banner to console
        self._print_startup_banner()
    
    def _print_startup_banner(self) -> None:
        """Print cinematic startup banner to console."""
        banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗    ██████╗ ██████╗  ██████╗    ║
║    ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝    ██╔══██╗██╔══██╗██╔═══██╗   ║
║    ██║  ███╗███████║██║   ██║███████╗   ██║       ██████╔╝██████╔╝██║   ██║   ║
║    ██║   ██║██╔══██║██║   ██║╚════██║   ██║       ██╔═══╝ ██╔══██╗██║   ██║   ║
║    ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║       ██║     ██║  ██║╚██████╔╝   ║
║     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝       ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ║
║                                                                               ║
║                        R A M - O N L Y   V A U L T                            ║
║                                                                               ║
║═══════════════════════════════════════════════════════════════════════════════║
║                                                                               ║
║  [SYSTEM] Initializing security protocols...                                  ║
║  [SYSTEM] AES-256 encryption module loaded                                    ║
║  [SYSTEM] Memory-only storage initialized                                     ║
║  [SYSTEM] Starting security monitors...                                       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def _build_header(self) -> None:
        """Build the header section."""
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.PANEL_BG,
            corner_radius=0,
            height=60
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        # Left side - Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="◢◤ GHOST-PROTOCOL v1.0 ◢◤",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=Colors.NEON_GREEN
        )
        self.title_label.pack(side="left", padx=20, pady=15)
        
        # Center - Classification
        self.classification_label = ctk.CTkLabel(
            self.header_frame,
            text="▓▓▓ TOP SECRET // NOFORN ▓▓▓",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=Colors.DANGER_RED
        )
        self.classification_label.pack(side="left", expand=True)
        
        # Right side - Time/Status indicator
        self.status_indicator = ctk.CTkLabel(
            self.header_frame,
            text="● ONLINE",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=Colors.NEON_GREEN
        )
        self.status_indicator.pack(side="right", padx=20)
    
    def _build_main_content(self) -> None:
        """Build the main content area."""
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BACKGROUND,
            corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Secret text area (expandable)
        self.secret_area = SecretTextArea(self.main_frame)
        self.secret_area.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right side - Status panel
        self.status_panel = StatusPanel(self.main_frame, width=220)
        self.status_panel.pack(side="right", fill="y")
        self.status_panel.pack_propagate(False)
    
    def _build_footer(self) -> None:
        """Build the footer with panic button."""
        self.footer_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.PANEL_BG,
            corner_radius=0,
            height=80
        )
        self.footer_frame.pack(fill="x")
        self.footer_frame.pack_propagate(False)
        
        # Left side - Instructions
        self.instructions_label = ctk.CTkLabel(
            self.footer_frame,
            text="[ESC] Emergency Wipe  |  [F1] Toggle Camera  |  [F2] Toggle USB Guard",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=Colors.TEXT_SECONDARY
        )
        self.instructions_label.pack(side="left", padx=20, pady=25)
        
        # Right side - PANIC BUTTON
        self.panic_button = ctk.CTkButton(
            self.footer_frame,
            text="⚠ EMERGENCY WIPE ⚠",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            fg_color=Colors.DANGER_RED,
            hover_color="#cc0033",
            text_color="#ffffff",
            corner_radius=0,
            width=200,
            height=50,
            command=self._on_panic_button
        )
        self.panic_button.pack(side="right", padx=20, pady=15)
        
        # Bind keyboard shortcuts
        self.bind("<Escape>", lambda e: self._on_panic_button())
    
    def _build_blur_overlay(self) -> None:
        """Build the privacy blur overlay."""
        self.blur_overlay = BlurOverlay(self)
    
    def _on_panic_button(self) -> None:
        """Handle panic button press."""
        print("")
        print("=" * 60)
        print("[CRITICAL] ████ MANUAL PANIC INITIATED ████")
        print("[CRITICAL] EMERGENCY WIPE BUTTON ACTIVATED!")
        print("[CRITICAL] INITIATING PROTOCOL 0.")
        print("=" * 60)
        print("")
        
        if self.panic_callback:
            self.panic_callback()
    
    def update_status(self, key: str, value: str) -> None:
        """Update a status panel indicator."""
        # Thread-safe status update
        self.after(0, lambda: self.status_panel.update_status(key, value))
    
    def set_blur(self, blur: bool) -> None:
        """Show or hide the privacy blur overlay."""
        def _update():
            if blur:
                self.blur_overlay.show()
                self._is_locked = True
            else:
                self.blur_overlay.hide()
                self._is_locked = False
        
        self.after(0, _update)
    
    def get_secret_text(self) -> str:
        """Get the current secret text."""
        return self.secret_area.get_text()
    
    def clear_secrets(self) -> None:
        """Clear the secret text area."""
        self.after(0, self.secret_area.clear)
    
    def show_wipe_animation(self) -> None:
        """Show a visual indication that memory is being wiped."""
        def _animate():
            # Flash red background
            self.configure(fg_color=Colors.DANGER_RED)
            self.update()
            self.after(100, lambda: self.configure(fg_color=Colors.BACKGROUND))
        
        self.after(0, _animate)
