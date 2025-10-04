# Line Art LoRA Training Pipeline

This guide explains how to turn cropped TaleKeeper line art into a LoRA adapter that can be used with Stable Diffusion checkpoints.

## Overview

1. Build a manifest describing the cropped training images.
2. Install the optional machine-learning dependencies.
3. Launch the LoRA training script to create weights and validation renders.
4. Load the resulting LoRA inside ComfyUI/Automatic1111 or the Stable Diffusion pipeline of your choice.

## 1. Build the manifest

The helper script scans a directory of cropped line art and creates a JSON file containing prompts for each image. Prompts default to a simple subject-based template, but you can customise them by editing the JSON after generation.

```bash
python scripts/lora_training/build_lineart_manifest.py assets/line_art_cropped \
  --output data/lora/lineart_manifest.json \
  --base-prompt "Clean black-and-white line art of {subject}, bold ink, comic shading" \
  --subject-template "{parent} {stem}" \
  --strip-prefix assets
```

- `--base-prompt` may contain a `{subject}` placeholder which will be replaced by an inferred subject derived from the filename/parent folder.
- `--strip-prefix` ensures image paths remain portable if you move the dataset (they become relative to the specified directory).
- The generated JSON is easy to hand-edit if you want to refine or override prompts on a per-image basis.

## 2. Install training dependencies

The core TaleKeeper app does not require GPU libraries, so LoRA-specific packages live in a separate `requirements-lora.txt` file. Install them into a dedicated virtual environment to keep the main dependency footprint small:

```bash
python -m venv .venv-lora
source .venv-lora/bin/activate
pip install -r requirements-lora.txt
```

> **Hardware requirements:** You will need a CUDA-capable GPU (12 GB VRAM or higher recommended) and the matching PyTorch build. CPU-only training is possible but extremely slow.

## 3. Train the LoRA

Run the training script with the manifest path. The defaults mirror the HuggingFace diffusers LoRA example but tuned for line art.

```bash
python scripts/lora_training/train_lineart_lora.py data/lora/lineart_manifest.json \
  --pretrained-model-name-or-path runwayml/stable-diffusion-v1-5 \
  --output-dir artifacts/lineart_lora \
  --train-batch-size 4 \
  --gradient-accumulation-steps 2 \
  --max-train-steps 3000 \
  --validation-prompt "clean black-and-white ink drawing of a heroic adventurer"
```

Key flags:

- `--rank` controls the LoRA rank (higher = more capacity, bigger file).
- `--learning-rate` and `--max-train-steps` determine training intensity.
- `--mixed-precision` can be set to `bf16`, `fp16`, or `no`.
- `--validation-prompt` optionally renders a sample image every `--validation-steps` into the output directory.

The script writes checkpoints under `artifacts/lineart_lora/` and saves final weights compatible with both diffusers and AUTOMATIC1111/ComfyUI LoRA loaders.

## 4. Using the LoRA

- **ComfyUI:** Drop the folder into `ComfyUI/models/loras/` and select it in your workflow.
- **AUTOMATIC1111:** Copy the generated `*.safetensors`/`adapter_config.json` pair into `stable-diffusion-webui/models/Lora/`.
- **Diffusers:** Use `pipe.load_lora_weights("artifacts/lineart_lora")` on any compatible pipeline.

## Troubleshooting

- If you see CUDA out-of-memory errors, reduce `--train-batch-size`, increase `--gradient-accumulation-steps`, or downscale `--resolution`.
- For better style consistency, edit prompts in the manifest to include tags such as `"ink wash"`, `"heavy contour"`, etc.
- To resume training from a checkpoint, pass `--checkpointing-steps` and point `accelerate launch` at the saved state directory.

Happy training!
