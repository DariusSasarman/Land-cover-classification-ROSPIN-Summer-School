import torch
import random
import numpy as np

from torch.amp import autocast


def seed_worker(worker_id):
    """

    Seed workers for NumPy/random.

    Called in PyTorch DataLoaders.

    """

    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


# Custom augmentation
def color_cast_approx(
    img: torch.Tensor, haze_intensity: float = 0.1, fixed_alpha: bool = False
) -> torch.Tensor:
    """

    Approximate blue hue color cast induced by atmospheric effects.

    Reference: figure 7 in EuroSAT paper.
    Note: expected input is float32 tensor in [0, 1] range.

    """

    if img.dtype == torch.uint8:
        sample = img.to(torch.float32) / 255.0

    elif img.dtype == torch.float32:
        sample = img

    else:
        raise TypeError(
            f"Unsupported input dtype: {img.dtype}. Expected torch.uint8 or torch.float32."
        )

    blue_tint = torch.tensor([0.6, 0.75, 1.0], device=img.device).view(
        3, 1, 1
    )  # alt: 0.5, 0.7, 1.0

    if fixed_alpha:
        alpha = haze_intensity

    else:
        alpha = torch.rand(1, device=img.device) * haze_intensity

    img_hazed = sample * (1 - alpha) + blue_tint * alpha

    return torch.clamp(img_hazed, 0.0, 1.0)  # Clamp: Ensure output in valid [0,1] range


# Augmentation upgrade
def d4_tta(model, img):
    """

    Test-Time Augmentation (TTA) helper function.

    Apply D4 group symmetries: rotations and horiziontal flips.
    Return averaged class logits.

    """

    views = []

    for k in range(4):
        # 90-degree rotations and horizontally flipped versions

        # Rotation: 0, 90, 180, 270 degrees
        r = torch.rot90(img, k=k, dims=(2, 3))
        views.append(model(r))
        
        # Horizontal flip
        f = torch.flip(r, dims=[3])
        views.append(model(f))

    # Return average logits
    return torch.stack(views, dim=0).mean(dim=0)  # logits (log-odds)


# Model eval fct.
def evaluate_model(model, dataloader, device, eval_approach="ref"):
    """

    Validation/eval runner that supports:
    Single-view ('ref') and multi-view Test-Time Augmentation ('tta').

    """

    model.eval()

    all_lbls = []
    all_prds = []

    use_cuda_amp = device.type == "cuda"

    # Notes
    #   - `torch.inference_mode()`:
    #       - backward graph not build; additional autograd skipped; tenors within may be inference-mode restricted
    #       - better default for final val/test eval (cf. "using inference tensors")
    #       - cf. https://docs.pytorch.org/docs/2.12/notes/autograd.html
    #   - `with torch.no_grad()`:
    #       - backward graph not build
    #       - otherwise normal tensors created

    # with torch.no_grad():
    with torch.inference_mode():
        for img, lbl in dataloader:
            img = img.to(device, non_blocking=True)
            lbl = lbl.to(device, non_blocking=True)

            # Mixed Precision
            with autocast(
                device_type=device.type,
                dtype=torch.float16,
                enabled=use_cuda_amp,
            ):
                # Reference (default)
                if eval_approach == "ref":
                    # p = torch.softmax(model(img), dim=1)  # for probability-like outputs (e.g. confidence/calibration/uncertainty/...)
                    p_ref = model(
                        img
                    )  # raw logits: sufficient for accuracy/precision/recall/F1/confusion matrix
                    p = p_ref

                # Test-Time Augementation (TTA)
                elif eval_approach == "tta":
                    # Direct approach (old version)
                    # p1 = torch.softmax(model(img), dim=1)  # Standard
                    # p2 = torch.softmax(model(torch.flip(img, [3])), dim=1)  # Horizontal-Flip
                    # p3 = torch.softmax(model(torch.flip(img, [2])), dim=1)  # Vertical-Fli
                    # p4 = torch.softmax(model(torch.rot90(img, 1, [2, 3])), dim=1)  # 90°-Rotation

                    # Averaged preds
                    # p_avg = (p1 + p2 + p3 + p4) / 4.0
                    p_avg = d4_tta(model, img)  # averaged logits
                    p = p_avg

                else:
                    raise ValueError(f"Unknown eval_approach: {eval_approach}")

            prd = p.argmax(1)

            all_lbls.extend(lbl.cpu().numpy())
            all_prds.extend(prd.cpu().numpy())

    return all_lbls, all_prds
