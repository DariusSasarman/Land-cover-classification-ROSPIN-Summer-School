import torch
import torch.nn as nn
from torchvision import models


def get_resnet_model(
    model_variant: str = "resnet18",
    num_classes: int = 10,
    use_architectural_mod: bool = True,
    stem_conv: str = "pretrained",
) -> nn.Module:
    """
    Construct ResNet backbone with ImageNet pretrained weights.
    Apply modifications for low-resolution EuroSAT image data (64x64).
    """

    try:
        model_constructor = getattr(models, model_variant)

        weights_id = f"ResNet{model_variant[6:]}_Weights"
        weights_constructor = getattr(models, weights_id)

        weights = weights_constructor.DEFAULT  # V1 ImageNet weights (IMAGENET1K_V1)

        model = model_constructor(weights=weights)

        print(
            f"Success Using Model: Loaded '{model_variant}' model variant and corresponding weights (ImageNet Pre-Training).\n"
        )

    except Exception as e:
        raise RuntimeError(
            f"Error: Invalid model ('{model_variant}') construction: {e}"
        )

    # Custom Architecture Modifications
    if use_architectural_mod:
        """
        (!) Change first convolutional layer to 3x3 kernel with stride 1
        - Default ResNet (7x7 kernel) is optimized for ImageNet images (224x224)
        - Attempt to preserve spatial resolution in low-res (64x64) EuroSAT images
        """

        conv_mod = nn.Conv2d(
            in_channels=3,
            out_channels=64,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False,
        )

        if stem_conv == "random":
            model.conv1 = conv_mod  # Replace with custom convolution

        elif stem_conv == "pretrained":
            # Conserve pre-training information by center-cropping 7x7 pre-trained filters
            pretrained_weights = (
                model.conv1.weight.detach().clone()
            )  # Shape: [64, 3, 7, 7]

            with torch.no_grad():
                conv_mod.weight.copy_(pretrained_weights[:, :, 2:5, 2:5])

            model.conv1 = conv_mod

        else:
            raise ValueError(f"Unknown stem_conv option: {stem_conv}")

        # Remove initial maxpool layer
        #   - Goal: Preserve spatial resolution
        model.maxpool = nn.Identity()

    # Re-initialize fully connected layer
    #   - Linear data transformation @ Final Layer w.r.t. EuroSAT class count
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    return model


def load_resnet_model(
    ckpt_path: str,
    device: torch.device,
    model_variant: str = "resnet18",
    num_classes: int = 10,
    use_architectural_mod: bool = True,
    stem_conv: str = "pretrained",
) -> nn.Module:
    """
    Instantiate model architecture.
    Load weights from checkpoint path.
    """

    model = get_resnet_model(
        model_variant=model_variant,
        num_classes=num_classes,
        use_architectural_mod=use_architectural_mod,
        stem_conv=stem_conv,
    )

    ckpt = torch.load(ckpt_path, map_location=device)

    if "model_state_dict" in ckpt:
        model.load_state_dict(ckpt["model_state_dict"])

    else:
        model.load_state_dict(ckpt)

    model.to(device)

    model.eval()

    return model
