"""Example script to train a custom Piper TTS voice for narration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from audio.piper_voice_trainer import (
    PiperVoiceTrainer,
    VoiceTrainingSample,
    create_sample_dataset_from_directory,
)


def main():
    print("=" * 60)
    print("Piper Voice Training - TaleKeeper Custom Narrator")
    print("=" * 60)

    audio_samples_dir = Path("training_samples/my_voice")
    transcript_file = audio_samples_dir / "transcripts.txt"

    if not audio_samples_dir.exists():
        print(f"\nError: Audio samples directory not found: {audio_samples_dir}")
        print("\nTo get started:")
        print("1. Create directory: training_samples/my_voice/")
        print("2. Add WAV files: 001.wav, 002.wav, etc.")
        print("3. Create transcripts.txt with format:")
        print("   001.wav|The text that was spoken in this file")
        print("   002.wav|Another transcript for the second file")
        return

    trainer = PiperVoiceTrainer(language="en-us")

    print("\nStep 1: Verifying training environment...")
    if not trainer.verify_training_environment():
        print("Setting up Piper training tools (this may take a few minutes)...")
        trainer.setup_training_environment()
        print("✓ Training environment ready")
    else:
        print("✓ Training environment already configured")

    print("\nStep 2: Loading audio samples...")
    samples = create_sample_dataset_from_directory(audio_samples_dir, transcript_file)
    print(f"✓ Loaded {len(samples)} samples")

    if len(samples) < 50:
        print(f"\n⚠ Warning: Only {len(samples)} samples found")
        print("  Recommended: 100+ for basic quality, 500+ for good quality")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return

    print("\nSample preview:")
    for i, sample in enumerate(samples[:3], 1):
        print(f"  {i}. {sample.audio_path.name}: {sample.transcript[:60]}...")

    print("\nStep 3: Preparing dataset...")
    dataset_dir = Path("training_data/my_custom_voice")
    metadata_path = trainer.prepare_dataset(
        samples,
        dataset_dir,
        sample_rate=22050,
        copy_audio=True,
    )
    print(f"✓ Dataset prepared in {dataset_dir}")

    print("\nStep 4: Training configuration")
    print("  Voice name: my_narrator")
    print("  Quality: medium")
    print("  Language: en-us")
    print(f"  Training samples: {len(samples)}")

    response = input("\nStart training? This will take several hours (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        print(f"Dataset is ready at: {dataset_dir}")
        print("You can train later with this dataset.")
        return

    print("\n" + "=" * 60)
    print("TRAINING STARTED - This will take several hours")
    print("=" * 60)

    output_dir = Path("excess/narration/models/my_custom_voice")

    try:
        model_path = trainer.train_voice(
            dataset_dir=dataset_dir,
            output_dir=output_dir,
            voice_name="my_narrator",
            quality="medium",
            epochs=200,
            batch_size=32,
        )

        print("\n" + "=" * 60)
        print("TRAINING COMPLETE!")
        print("=" * 60)
        print(f"\nModel saved to: {model_path}")

        print("\nNext steps:")
        print("1. Add to voice_profiles.json:")
        print('   {')
        print('     "voice_id": "my_narrator",')
        print('     "campaign_style": "custom",')
        print(f'     "model_path": "{model_path}",')
        print('     "style": { "speaking_rate": 1.0 }')
        print('   }')
        print("\n2. Restart TaleKeeper")
        print("3. Test your custom voice!")

    except Exception as e:
        print(f"\n✗ Training failed: {e}")
        print("\nCheck the error above for details.")
        print("Common issues:")
        print("  - GPU out of memory: reduce batch_size")
        print("  - Missing dependencies: pip install -r requirements.txt")
        print("  - Bad audio files: check WAV format and sample rate")


if __name__ == "__main__":
    main()
