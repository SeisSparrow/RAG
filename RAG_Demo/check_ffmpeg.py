#!/usr/bin/env python3
"""
Check if ffmpeg is available for audio processing
"""

import subprocess
import sys

def check_ffmpeg():
    """Check if ffmpeg is installed and accessible"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg is installed and working")
            return True
        else:
            print("❌ ffmpeg is not working properly")
            return False
    except FileNotFoundError:
        print("❌ ffmpeg is not installed")
        return False

def install_ffmpeg_instructions():
    """Provide installation instructions for ffmpeg"""
    print("\n📋 To install ffmpeg:")
    print("macOS: brew install ffmpeg")
    print("Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
    print("Windows: Download from https://ffmpeg.org/download.html")
    print("\nAfter installation, run this script again to verify.")

if __name__ == "__main__":
    print("🔍 Checking ffmpeg installation...")
    
    if check_ffmpeg():
        print("🎉 ffmpeg is ready for audio processing!")
    else:
        install_ffmpeg_instructions()
        sys.exit(1)
