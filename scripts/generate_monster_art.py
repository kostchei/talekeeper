"""Generate black and white line art for monster cards using Stable Diffusion + LoRA.

This script:
1. Pulls monsters sequentially from the database
2. Generates campaign-aware descriptions using Ollama (via CampaignDescriptionService)
3. Creates 80x60 black and white line art images using Stable Diffusion with the trained LoRA
4. Saves images to data/images/monsters/ directory for use in monster cards

Monster card dimensions: 80x60 pixels (from encounter_panel.py:4895)
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
from peft import PeftModel


sys.path.insert(0, str(Path(__file__).parent.parent))

from services.campaign_description_service import CampaignDescriptionService
from encounter_pane.campaign_frame import CampaignFrame


def load_campaign_frame(campaign_path: str) -> tuple[CampaignFrame, str]:
    """Load campaign frame data from JSON file and return frame + campaign name."""
    with open(campaign_path, 'r', encoding='utf-8') as f:
        campaign_data = json.load(f)
    campaign_name = campaign_data.get('name', Path(campaign_path).stem)
    return CampaignFrame(campaign_data), campaign_name


def load_monsters_from_db(db_path: str = "talekeeper.db", limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Load monster data from SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM monsters ORDER BY challenge_rating, name"
    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query)
    monsters = []
    for row in cursor.fetchall():
        monsters.append({
            'id': row['id'],
            'name': row['name'],
            'type': row['type'],
            'subtype': row['subtype'],
            'size': row['size'],
            'alignment': row['alignment'],
            'challenge_rating': row['challenge_rating'],
            'cr_str': row['challenge_rating'],
            'hit_points': row['hit_points'],
            'armor_class': row['armor_class'],
            'special_abilities': row['special_abilities'],
            'actions': row['actions'],
        })

    conn.close()
    return monsters


def generate_monster_description(
    monster: Dict[str, Any],
    campaign_frame: CampaignFrame,
    description_service: CampaignDescriptionService
) -> str:
    """Generate campaign-aware description for monster using Ollama."""
    description = description_service.generate_description(
        entity_type="monster",
        entity_data=monster,
        campaign_frame=campaign_frame
    )
    return description or f"{monster['name']}, a {monster['type']}"


def create_lineart_prompt(monster: Dict[str, Any], description: str) -> str:
    """Create prompt optimized for old school D&D black and white line art."""
    creature_type = monster.get('type', 'creature').lower()
    monster_name = monster.get('name', 'creature')

    prompt = f"1980s D&D Monster Manual, {creature_type} {monster_name}, pen and ink, crosshatching, white background"

    return prompt


def generate_monster_image(
    prompt: str,
    pipeline: StableDiffusionPipeline,
    width: int = 80,
    height: int = 60,
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None
) -> tuple[Image.Image, Image.Image]:
    """Generate monster image at high-res then downscale. Returns (full_res, thumbnail)."""
    generator = torch.Generator(device=pipeline.device)
    if seed is not None:
        generator.manual_seed(seed)

    negative_prompt = "color, colored, photorealistic, photograph, digital art, 3d render, blur, text, watermark, modern style, words, boxes, letters, numbers, writing"

    gen_width = 320
    gen_height = 240

    result = pipeline(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        generator=generator,
        width=gen_width,
        height=gen_height,
    )

    image = result.images[0]
    image = image.convert('L').convert('RGB')

    thumbnail = image.resize((width, height), Image.Resampling.LANCZOS)

    return image, thumbnail


def setup_pipeline(
    model_path: str = "runwayml/stable-diffusion-v1-5",
    lora_path: Optional[str] = None,
    lora_scale: float = 1.0,
    device: str = "cuda"
) -> StableDiffusionPipeline:
    """Setup Stable Diffusion pipeline with optional LoRA."""
    print(f"Loading base model: {model_path}")

    pipeline = StableDiffusionPipeline.from_pretrained(
        model_path,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        safety_checker=None,
    )

    pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)

    if lora_path and os.path.exists(lora_path):
        print(f"Loading LoRA adapter from: {lora_path} (scale: {lora_scale})")
        pipeline.unet = PeftModel.from_pretrained(pipeline.unet, lora_path)
        if hasattr(pipeline.unet, 'set_adapters'):
            pipeline.unet.set_adapters(["default"], weights=[lora_scale])
        elif lora_scale != 1.0:
            for name, module in pipeline.unet.named_modules():
                if hasattr(module, 'scaling'):
                    module.scaling['default'] = lora_scale

    pipeline = pipeline.to(device)
    pipeline.enable_attention_slicing()

    if device == "cuda":
        try:
            pipeline.enable_xformers_memory_efficient_attention()
        except Exception as e:
            print(f"Could not enable xformers: {e}")

    return pipeline


def sanitize_filename(name: str) -> str:
    """Convert monster name to safe filename."""
    safe = name.lower().replace(' ', '_').replace("'", '').replace('"', '')
    safe = ''.join(c for c in safe if c.isalnum() or c == '_')
    return safe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--campaign",
        type=str,
        default="encounter_pane/campaign/golden.json",
        help="Path to campaign frame JSON file"
    )
    parser.add_argument(
        "--database",
        type=str,
        default="talekeeper.db",
        help="Path to SQLite database"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/images/monsters",
        help="Output directory for generated images"
    )
    parser.add_argument(
        "--lora-path",
        type=str,
        default="artifacts/lineart_lora",
        help="Path to trained LoRA adapter"
    )
    parser.add_argument(
        "--lora-scale",
        type=float,
        default=0.3,
        help="LoRA strength/scale (0.0-1.0, default 0.3)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="runwayml/stable-diffusion-v1-5",
        help="Base Stable Diffusion model"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of monsters to process"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=80,
        help="Output image width"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=60,
        help="Output image height"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to run inference on"
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://127.0.0.1:11434",
        help="Ollama API base URL"
    )
    parser.add_argument(
        "--ollama-model",
        type=str,
        default="mistral:7b-instruct",
        help="Ollama model for descriptions"
    )

    args = parser.parse_args()

    print("Loading campaign frame...")
    campaign_frame, campaign_name = load_campaign_frame(args.campaign)
    campaign_safe_name = sanitize_filename(campaign_name)

    campaign_output_dir = os.path.join(args.output_dir, campaign_safe_name)
    os.makedirs(campaign_output_dir, exist_ok=True)
    print(f"Output directory: {campaign_output_dir}")

    print("Initializing description service...")
    description_service = CampaignDescriptionService(
        base_url=args.ollama_url,
        default_model=args.ollama_model
    )

    print("Loading monsters from database...")
    monsters = load_monsters_from_db(args.database, args.limit)
    print(f"Found {len(monsters)} monsters")

    print("Setting up Stable Diffusion pipeline...")
    pipeline = setup_pipeline(
        model_path=args.model,
        lora_path=args.lora_path if os.path.exists(args.lora_path) else None,
        lora_scale=args.lora_scale,
        device=args.device
    )

    print("\nStarting image generation...")
    for i, monster in enumerate(monsters, 1):
        monster_name = monster['name']
        safe_name = sanitize_filename(monster_name)
        output_path = os.path.join(campaign_output_dir, f"{safe_name}.png")

        if os.path.exists(output_path):
            print(f"[{i}/{len(monsters)}] Skipping {monster_name} (already exists)")
            continue

        print(f"\n[{i}/{len(monsters)}] Processing: {monster_name}")
        print(f"  CR: {monster['challenge_rating']}, Type: {monster['type']}")

        print("  Generating description with Ollama...")
        description = generate_monster_description(monster, campaign_frame, description_service)
        print(f"  Description: {description[:100]}...")

        print("  Creating line art prompt...")
        prompt = create_lineart_prompt(monster, description)
        print(f"  Prompt: {prompt[:100]}...")

        print("  Generating image with Stable Diffusion...")
        full_image, thumbnail = generate_monster_image(
            prompt=prompt,
            pipeline=pipeline,
            width=args.width,
            height=args.height,
            seed=args.seed
        )

        full_path = output_path.replace('.png', '_full.png')
        print(f"  Saving full-res to: {full_path}")
        full_image.save(full_path)
        print(f"  Saving thumbnail to: {output_path}")
        thumbnail.save(output_path)

    print(f"\n\nComplete! Generated images in {campaign_output_dir}")


if __name__ == "__main__":
    main()
