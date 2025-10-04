# Monster Art Generation

This guide explains how to generate black and white line art for monster cards using the trained LoRA adapter and Ollama for campaign-aware descriptions.

## Overview

The monster art generation system:
1. Pulls monsters sequentially from the database
2. Generates campaign-aware descriptions using Ollama
3. Creates 320x240 black and white line art using Stable Diffusion + LoRA
4. Downscales to 80x60 thumbnails for monster cards
5. Saves both full-resolution and thumbnail images

## Prerequisites

### 1. Trained LoRA Adapter
First, train the line art LoRA adapter (see [lineart_lora_training.md](lineart_lora_training.md)):

```bash
conda activate lora
python scripts/lora_training/train_lineart_lora.py data/lora/lineart_manifest.json \
  --max-train-steps 500 \
  --output-dir artifacts/lineart_lora
```

This creates a lightweight adapter (~6MB) without intermediate checkpoints.

### 2. Ollama Running
Ensure Ollama is running with mistral:7b-instruct:

```bash
ollama serve  # Run in background
ollama pull mistral:7b-instruct
```

### 3. Conda Environment
Use the `lora` environment which has PyTorch and diffusers:

```bash
conda activate lora
```

## Generating Monster Art

### Basic Usage

Generate monsters for a specific campaign:

```bash
conda activate lora
python scripts/generate_monster_art.py \
  --campaign encounter_pane/campaign/golden.json \
  --limit 10
```

### Campaign-Specific Generation

Each campaign gets its own folder with tailored descriptions:

```bash
# Golden Age campaign (high magic, legendary themes)
python scripts/generate_monster_art.py \
  --campaign encounter_pane/campaign/golden.json

# Conan campaign (sword & sorcery themes)
python scripts/generate_monster_art.py \
  --campaign encounter_pane/campaign/conan.json
```

### LoRA Strength Adjustment

Control how much the LoRA influences the output (default: 0.3):

```bash
# Lighter LoRA influence (20%)
python scripts/generate_monster_art.py \
  --campaign encounter_pane/campaign/golden.json \
  --lora-scale 0.2

# Medium influence (30% - default)
python scripts/generate_monster_art.py \
  --campaign encounter_pane/campaign/golden.json \
  --lora-scale 0.3

# Stronger influence (50%)
python scripts/generate_monster_art.py \
  --campaign encounter_pane/campaign/golden.json \
  --lora-scale 0.5
```

### Full Parameter List

```bash
python scripts/generate_monster_art.py \
  --campaign encounter_pane/campaign/golden.json \
  --database talekeeper.db \
  --output-dir data/images/monsters \
  --lora-path artifacts/lineart_lora \
  --lora-scale 0.3 \
  --model runwayml/stable-diffusion-v1-5 \
  --limit 50 \
  --width 80 \
  --height 60 \
  --seed 42 \
  --device cuda \
  --ollama-url http://127.0.0.1:11434 \
  --ollama-model mistral:7b-instruct
```

## Output Structure

Images are saved in campaign-specific folders:

```
data/images/monsters/
├── golden_age/
│   ├── awakened_shrub.png          # 80x60 thumbnail for UI
│   ├── awakened_shrub_full.png     # 320x240 full resolution
│   ├── baboon.png
│   ├── baboon_full.png
│   └── ...
└── conan/
    ├── awakened_shrub.png
    ├── awakened_shrub_full.png
    └── ...
```

## Art Style

### Prompts
Images use 1980s D&D Monster Manual style:
- "1980s D&D Monster Manual illustration"
- "black and white ink drawing"
- "crosshatching, pen and ink"
- "fantasy RPG art, old school revival style"
- "detailed linework, white background"

### Negative Prompts
Explicitly blocks unwanted elements:
- "color, colored"
- "photorealistic, photograph"
- "digital art, 3d render"
- "text, words, boxes, letters, numbers, writing"
- "modern style"

## Campaign-Aware Descriptions

Ollama generates descriptions tailored to each campaign's theme:

**Golden Age (high magic):**
> "In epic forests where legends are born, the Awakened Shrub stands sentinel. Its gnarled roots entwine with arcane power, imbued with the ability to drain life..."

**Conan (sword & sorcery):**
> "In the savage wilderness, the Awakened Shrub lurks. A twisted remnant of fell sorcery, its thorned branches thirst for blood..."

## Performance Notes

### Generation Speed
- ~30 seconds per monster (30 inference steps at 320x240)
- RTX 4090: ~1.1 iterations/second
- Batch processing recommended for full database

### Memory Requirements
- GPU: 12GB VRAM minimum (24GB recommended)
- RAM: 16GB minimum
- Disk: ~100KB per monster (full + thumbnail)

## Troubleshooting

### Ollama Connection Errors
```
[LLM] Ollama request failed: 404 Client Error
```

**Solution:** Ensure Ollama is running and model is available:
```bash
ollama serve
ollama list  # Check installed models
ollama pull mistral:7b-instruct  # Install if needed
```

### CUDA Errors
```
OSError: Error loading "torch\lib\c10_cuda.dll"
```

**Solution:** Activate the lora environment:
```bash
conda activate lora
```

### Text in Images
If text/boxes appear in generated images, the negative prompt should block them. If persisting, retrain the LoRA with better training data or increase the negative prompt weight.

### LoRA Too Strong/Weak
Adjust `--lora-scale`:
- Too strong (over-processed): Try 0.2-0.3
- Too weak (not enough style): Try 0.4-0.5
- Default: 0.3 (30%)

## Integration with TaleKeeper

Monster cards automatically load images from:
```python
image_path = f"data/images/monsters/{campaign_name}/{monster_name}.png"
```

The encounter panel checks this path and displays the 80x60 thumbnail on monster cards during combat.

## Next Steps

1. Generate art for primary campaign
2. Review quality and adjust LoRA scale if needed
3. Generate art for additional campaigns
4. Optionally retrain LoRA with more training data for better consistency
