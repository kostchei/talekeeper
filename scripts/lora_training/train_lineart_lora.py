"""Train a Stable Diffusion LoRA adapter on cropped line-art images."""
from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

import torch
import torch.nn.functional as F
from accelerate import Accelerator
from accelerate.logging import get_logger
from accelerate.utils import ProjectConfiguration, set_seed
from diffusers import AutoencoderKL, DDPMScheduler, UNet2DConditionModel
from diffusers.loaders import AttnProcsLayers
from diffusers.models.attention_processor import LoRAAttnProcessor
from diffusers.optimization import get_scheduler
from diffusers.utils.import_utils import is_xformers_available
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.transforms import InterpolationMode
from transformers import CLIPTextModel, CLIPTokenizer

logger = get_logger(__name__)


@dataclass
class TrainingExample:
    image_path: str
    prompt: str
    negative_prompt: str | None = None


class LineArtDataset(Dataset):
    def __init__(
        self,
        entries: Sequence[TrainingExample],
        tokenizer: CLIPTokenizer,
        resolution: int,
        center_crop: bool,
        random_flip: bool,
        fallback_prompt: str,
    ) -> None:
        self.entries = entries
        self.tokenizer = tokenizer
        interpolation = InterpolationMode.BILINEAR
        t: List[Any] = [transforms.Resize(resolution, interpolation=interpolation)]
        if center_crop:
            t.append(transforms.CenterCrop(resolution))
        else:
            t.append(transforms.RandomCrop(resolution))
        if random_flip:
            t.append(transforms.RandomHorizontalFlip())
        t.extend(
            [
                transforms.ToTensor(),
                transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
            ]
        )
        self.image_transforms = transforms.Compose(t)
        self.fallback_prompt = fallback_prompt

    def __len__(self) -> int:
        return len(self.entries)

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        example = self.entries[index]
        with Image.open(example.image_path) as image:
            image = image.convert("RGB")
            pixel_values = self.image_transforms(image)
        # PIL closes file automatically via context manager.
        prompt = example.prompt or self.fallback_prompt
        encoded = self.tokenizer(
            prompt,
            truncation=True,
            padding="max_length",
            max_length=self.tokenizer.model_max_length,
            return_tensors="pt",
        )
        return {
            "pixel_values": pixel_values,
            "input_ids": encoded.input_ids[0],
            "attention_mask": encoded.attention_mask[0],
        }


@dataclass
class TrainConfig:
    pretrained_model_name_or_path: str
    manifest_path: Path
    output_dir: Path
    resolution: int = 512
    center_crop: bool = True
    random_flip: bool = False
    learning_rate: float = 1e-4
    train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    lr_scheduler: str = "cosine"
    lr_warmup_steps: int = 500
    max_train_steps: int = 2000
    checkpointing_steps: int = 500
    validation_prompt: str | None = None
    validation_steps: int = 500
    seed: int = 42
    rank: int = 8
    mixed_precision: str | None = "fp16"
    use_8bit_adam: bool = False
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999
    adam_weight_decay: float = 1e-2
    adam_epsilon: float = 1e-8
    max_grad_norm: float = 1.0
    report_to: Sequence[str] | None = None
    fallback_prompt: str = "clean black and white line art"

    @staticmethod
    def from_args(args: argparse.Namespace) -> "TrainConfig":
        return TrainConfig(
            pretrained_model_name_or_path=args.pretrained_model_name_or_path,
            manifest_path=args.manifest,
            output_dir=args.output_dir,
            resolution=args.resolution,
            center_crop=args.center_crop,
            random_flip=args.random_flip,
            learning_rate=args.learning_rate,
            train_batch_size=args.train_batch_size,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            lr_scheduler=args.lr_scheduler,
            lr_warmup_steps=args.lr_warmup_steps,
            max_train_steps=args.max_train_steps,
            checkpointing_steps=args.checkpointing_steps,
            validation_prompt=args.validation_prompt,
            validation_steps=args.validation_steps,
            seed=args.seed,
            rank=args.rank,
            mixed_precision=args.mixed_precision,
            use_8bit_adam=args.use_8bit_adam,
            adam_beta1=args.adam_beta1,
            adam_beta2=args.adam_beta2,
            adam_weight_decay=args.adam_weight_decay,
            adam_epsilon=args.adam_epsilon,
            max_grad_norm=args.max_grad_norm,
            report_to=args.report_to,
            fallback_prompt=args.fallback_prompt,
        )


def read_manifest(path: Path) -> List[TrainingExample]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    entries: List[TrainingExample] = []
    for item in data:
        image_path = Path(item["image_path"])
        if not image_path.is_absolute():
            image_path = path.parent / image_path
        if not image_path.exists():
            raise FileNotFoundError(f"Referenced image not found: {image_path}")
        entries.append(
            TrainingExample(
                image_path=str(image_path),
                prompt=item.get("prompt", ""),
                negative_prompt=item.get("negative_prompt"),
            )
        )
    if not entries:
        raise ValueError("Manifest did not contain any entries")
    return entries


def collate_fn(examples: Sequence[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
    pixel_values = torch.stack([example["pixel_values"] for example in examples])
    input_ids = torch.stack([example["input_ids"] for example in examples])
    attention_mask = torch.stack([example["attention_mask"] for example in examples])
    return {
        "pixel_values": pixel_values,
        "input_ids": input_ids,
        "attention_mask": attention_mask,
    }


def create_attn_procs(unet: UNet2DConditionModel, rank: int) -> AttnProcsLayers:
    lora_attn_procs = {}
    for name in unet.attn_processors.keys():
        cross_attention_dim = None if name.endswith("attn1.processor") else unet.config.cross_attention_dim
        if name.startswith("mid_block"):
            hidden_size = unet.config.block_out_channels[-1]
        elif name.startswith("up_blocks"):
            block_id = int(name[len("up_blocks.")])
            hidden_size = unet.config.block_out_channels[-(block_id + 1)]
        elif name.startswith("down_blocks"):
            block_id = int(name[len("down_blocks.")])
            hidden_size = unet.config.block_out_channels[block_id]
        else:
            raise ValueError(f"Unexpected attention processor name: {name}")
        lora_attn_procs[name] = LoRAAttnProcessor(
            hidden_size=hidden_size,
            cross_attention_dim=cross_attention_dim,
            rank=rank,
        )
    unet.set_attn_processor(lora_attn_procs)
    return AttnProcsLayers(unet.attn_processors)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to the JSON manifest created by build_lineart_manifest.py")
    parser.add_argument("--pretrained-model-name-or-path", type=str, default="runwayml/stable-diffusion-v1-5")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/lineart_lora"))
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--center-crop", action="store_true")
    parser.add_argument("--no-center-crop", dest="center_crop", action="store_false")
    parser.set_defaults(center_crop=True)
    parser.add_argument("--random-flip", action="store_true", default=False)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--train-batch-size", type=int, default=2)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--lr-scheduler", type=str, default="cosine")
    parser.add_argument("--lr-warmup-steps", type=int, default=500)
    parser.add_argument("--max-train-steps", type=int, default=2000)
    parser.add_argument("--checkpointing-steps", type=int, default=500)
    parser.add_argument("--validation-prompt", type=str, default=None)
    parser.add_argument("--validation-steps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--rank", type=int, default=8)
    parser.add_argument("--mixed-precision", type=str, choices=["no", "fp16", "bf16"], default="fp16")
    parser.add_argument("--use-8bit-adam", action="store_true", default=False)
    parser.add_argument("--adam-beta1", type=float, default=0.9)
    parser.add_argument("--adam-beta2", type=float, default=0.999)
    parser.add_argument("--adam-weight-decay", type=float, default=1e-2)
    parser.add_argument("--adam-epsilon", type=float, default=1e-8)
    parser.add_argument("--max-grad-norm", type=float, default=1.0)
    parser.add_argument("--report-to", nargs="*", default=None)
    parser.add_argument("--fallback-prompt", type=str, default="clean black and white line art")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = TrainConfig.from_args(args)

    accelerator = Accelerator(
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        mixed_precision=None if config.mixed_precision == "no" else config.mixed_precision,
        log_with=config.report_to,
        project_config=ProjectConfiguration(project_dir=str(config.output_dir), logging_dir=str(config.output_dir / "logs")),
    )

    tracker_config = asdict(config)
    tracker_config["manifest_path"] = str(config.manifest_path)
    tracker_config["output_dir"] = str(config.output_dir)

    if accelerator.is_main_process:
        os.makedirs(config.output_dir, exist_ok=True)
        with (config.output_dir / "train_config.json").open("w", encoding="utf-8") as f:
            json.dump(tracker_config, f, indent=2)
    accelerator.wait_for_everyone()
    if config.report_to:
        accelerator.init_trackers("lineart-lora", tracker_config)

    logger.info("Loading tokenizer and text encoder")
    tokenizer = CLIPTokenizer.from_pretrained(config.pretrained_model_name_or_path, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(config.pretrained_model_name_or_path, subfolder="text_encoder")

    logger.info("Loading VAE and UNet")
    vae = AutoencoderKL.from_pretrained(config.pretrained_model_name_or_path, subfolder="vae")
    unet = UNet2DConditionModel.from_pretrained(config.pretrained_model_name_or_path, subfolder="unet")

    noise_scheduler = DDPMScheduler.from_pretrained(config.pretrained_model_name_or_path, subfolder="scheduler")

    if config.seed is not None:
        set_seed(config.seed)

    entries = read_manifest(config.manifest_path)
    dataset = LineArtDataset(
        entries=entries,
        tokenizer=tokenizer,
        resolution=config.resolution,
        center_crop=config.center_crop,
        random_flip=config.random_flip,
        fallback_prompt=config.fallback_prompt,
    )

    train_dataloader = DataLoader(
        dataset,
        shuffle=True,
        batch_size=config.train_batch_size,
        collate_fn=collate_fn,
        num_workers=min(8, os.cpu_count() or 1),
    )

    if is_xformers_available():
        logger.info("Enabling xFormers memory efficient attention")
        unet.enable_xformers_memory_efficient_attention()

    weight_dtype = torch.float32
    if accelerator.mixed_precision == "fp16":
        weight_dtype = torch.float16
    elif accelerator.mixed_precision == "bf16":
        weight_dtype = torch.bfloat16

    vae.requires_grad_(False)
    vae.to(accelerator.device, dtype=weight_dtype)
    text_encoder.requires_grad_(False)
    text_encoder.to(accelerator.device, dtype=weight_dtype)
    unet.requires_grad_(False)

    lora_layers = create_attn_procs(unet, config.rank)
    lora_layers.to(accelerator.device)

    if config.use_8bit_adam:
        try:
            import bitsandbytes as bnb

            optimizer = bnb.optim.AdamW8bit(
                lora_layers.parameters(),
                lr=config.learning_rate,
                betas=(config.adam_beta1, config.adam_beta2),
                weight_decay=config.adam_weight_decay,
                eps=config.adam_epsilon,
            )
        except ImportError as exc:
            raise RuntimeError("bitsandbytes must be installed to use 8-bit Adam") from exc
    else:
        optimizer = torch.optim.AdamW(
            lora_layers.parameters(),
            lr=config.learning_rate,
            betas=(config.adam_beta1, config.adam_beta2),
            weight_decay=config.adam_weight_decay,
            eps=config.adam_epsilon,
        )

    lr_scheduler = get_scheduler(
        config.lr_scheduler,
        optimizer=optimizer,
        num_warmup_steps=config.lr_warmup_steps,
        num_training_steps=config.max_train_steps,
    )

    lora_layers, optimizer, train_dataloader, lr_scheduler = accelerator.prepare(
        lora_layers, optimizer, train_dataloader, lr_scheduler
    )
    unet, text_encoder, vae = accelerator.prepare(unet, text_encoder, vae)
    unet.to(accelerator.device, dtype=weight_dtype)
    text_encoder.to(accelerator.device, dtype=weight_dtype)
    vae.to(accelerator.device, dtype=weight_dtype)

    total_batch_size = config.train_batch_size * accelerator.num_processes * config.gradient_accumulation_steps
    logger.info(f"***** Running training *****")
    logger.info(f"  Num batches each epoch = {len(train_dataloader)}")
    logger.info(f"  Total optimization steps = {config.max_train_steps}")
    logger.info(f"  Total train batch size (w. parallel, distributed & accumulation) = {total_batch_size}")

    global_step = 0
    for epoch in range(math.ceil(config.max_train_steps / len(train_dataloader))):
        for step, batch in enumerate(train_dataloader):
            with accelerator.accumulate(lora_layers):
                pixel_values = batch["pixel_values"].to(device=accelerator.device, dtype=weight_dtype)
                with torch.no_grad():
                    latents = vae.encode(pixel_values).latent_dist.sample()
                latents = latents * vae.config.scaling_factor
                noise = torch.randn_like(latents)
                timesteps = torch.randint(
                    0, noise_scheduler.config.num_train_timesteps, (latents.shape[0],), device=latents.device
                ).long()
                noisy_model_input = noise_scheduler.add_noise(latents, noise, timesteps)
                encoder_hidden_states = text_encoder(
                    batch["input_ids"].to(device=accelerator.device),
                    attention_mask=batch["attention_mask"].to(device=accelerator.device),
                )[0]
                model_pred = unet(noisy_model_input, timesteps, encoder_hidden_states).sample
                if noise_scheduler.config.prediction_type == "epsilon":
                    target = noise
                elif noise_scheduler.config.prediction_type == "v_prediction":
                    target = noise_scheduler.get_velocity(latents, noise, timesteps)
                else:
                    raise ValueError(f"Unknown prediction type {noise_scheduler.config.prediction_type}")
                loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")

                accelerator.backward(loss)

                if accelerator.sync_gradients:
                    accelerator.clip_grad_norm_(lora_layers.parameters(), config.max_grad_norm)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()

            if accelerator.sync_gradients:
                global_step += 1
                accelerator.log({"train_loss": loss.detach().item()}, step=global_step)
                if accelerator.is_main_process and config.checkpointing_steps and global_step % config.checkpointing_steps == 0:
                    save_path = config.output_dir / f"checkpoint-{global_step}"
                    accelerator.save_state(str(save_path))

            if global_step >= config.max_train_steps:
                break

        logger.info(f"Epoch {epoch} complete, global step {global_step}")
        if global_step >= config.max_train_steps:
            break

        if (
            accelerator.is_main_process
            and config.validation_prompt
            and config.validation_steps
            and global_step % config.validation_steps == 0
        ):
            generate_validation_image(
                config=config,
                accelerator=accelerator,
                text_encoder=text_encoder,
                tokenizer=tokenizer,
                unet=unet,
                vae=vae,
            )

    accelerator.wait_for_everyone()

    if accelerator.is_main_process:
        logger.info("Saving LoRA weights")
        lora_layers.save_pretrained(config.output_dir, safe_serialization=True)

    accelerator.end_training()


def generate_validation_image(
    *,
    config: TrainConfig,
    accelerator: Accelerator,
    text_encoder: CLIPTextModel,
    tokenizer: CLIPTokenizer,
    unet: UNet2DConditionModel,
    vae: AutoencoderKL,
) -> None:
    from diffusers import StableDiffusionPipeline

    pipeline = StableDiffusionPipeline.from_pretrained(
        config.pretrained_model_name_or_path,
        torch_dtype=unet.dtype,
    )
    pipeline.unet = accelerator.unwrap_model(unet)
    pipeline.text_encoder = accelerator.unwrap_model(text_encoder)
    pipeline.vae = accelerator.unwrap_model(vae)
    pipeline.to(accelerator.device)
    pipeline.set_progress_bar_config(disable=True)

    generator = torch.Generator(device=accelerator.device)
    if config.seed is not None:
        generator.manual_seed(config.seed)
    prompt = config.validation_prompt or config.fallback_prompt
    images = pipeline(prompt=prompt, num_inference_steps=30, guidance_scale=7.5, generator=generator).images
    image = images[0]
    output_path = config.output_dir / "validation.png"
    image.save(output_path)
    logger.info("Saved validation image to %s", output_path)


if __name__ == "__main__":
    main()
