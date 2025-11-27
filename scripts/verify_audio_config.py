import sys
import os
from dataclasses import asdict

# Add src to path
sys.path.append(os.path.abspath("src"))

from talekeeper.core.config import ConfigManager, AudioConfig

def verify_audio_config():
    print("--- Verifying Audio Configuration ---")
    
    # 1. Test Default Config
    config_manager = ConfigManager("test_config.json")
    # Reset to defaults to ensure clean state
    config_manager.reset_to_defaults()
    
    audio_config = config_manager.audio
    print(f"Default Audio Config: {audio_config}")
    
    assert audio_config.enable_master_audio == True
    assert audio_config.enable_music == True
    assert audio_config.enable_narration == True
    assert audio_config.master_volume == 1.0
    assert audio_config.music_volume == 0.4
    assert audio_config.narration_volume == 0.7
    print("✅ Default configuration verified")

    # 2. Test Modifying Config
    print("\n--- Modifying Configuration ---")
    config_manager.audio.enable_master_audio = False
    config_manager.audio.music_volume = 0.8
    config_manager.save_config()
    
    # Reload to verify persistence
    new_manager = ConfigManager("test_config.json")
    print(f"Reloaded Audio Config: {new_manager.audio}")
    
    assert new_manager.audio.enable_master_audio == False
    assert new_manager.audio.music_volume == 0.8
    print("✅ Configuration persistence verified")
    
    # Cleanup
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    print("\n✅ All configuration tests passed!")

if __name__ == "__main__":
    verify_audio_config()
