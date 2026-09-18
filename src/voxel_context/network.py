from __future__ import annotations


DEFAULT_MODEL_ARCHITECTURE = "unet3d_baseline"
RESIDUAL_UNET3D_ARCHITECTURE = "res_unet3d"
SUPPORTED_MODEL_ARCHITECTURES = (DEFAULT_MODEL_ARCHITECTURE, RESIDUAL_UNET3D_ARCHITECTURE)


def _torch_import():
    try:
        import torch
        import torch.nn as nn
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("PyTorch is not available in this interpreter.") from exc
    return torch, nn


def normalize_model_architecture(architecture: object = None) -> str:
    value = str(architecture or DEFAULT_MODEL_ARCHITECTURE).strip().lower()
    if not value:
        value = DEFAULT_MODEL_ARCHITECTURE
    aliases = {
        "baseline": DEFAULT_MODEL_ARCHITECTURE,
        "unet3d": DEFAULT_MODEL_ARCHITECTURE,
        "default": DEFAULT_MODEL_ARCHITECTURE,
    }
    value = aliases.get(value, value)
    if value not in SUPPORTED_MODEL_ARCHITECTURES:
        supported = ", ".join(SUPPORTED_MODEL_ARCHITECTURES)
        raise ValueError(f"Unsupported model architecture: {architecture!r}. Supported: {supported}.")
    return value


def make_unet3d(
    *,
    in_channels: int,
    num_classes: int,
    base_channels: int = 24,
) -> object:
    torch, nn = _torch_import()

    def make_norm(channels: int) -> object:
        groups = min(8, int(channels))
        while groups > 1 and channels % groups != 0:
            groups -= 1
        return nn.GroupNorm(groups, channels)

    class ConvBlock(nn.Module):
        def __init__(self, c_in: int, c_out: int) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv3d(c_in, c_out, kernel_size=3, padding=1, bias=False),
                make_norm(c_out),
                nn.ReLU(inplace=True),
                nn.Conv3d(c_out, c_out, kernel_size=3, padding=1, bias=False),
                make_norm(c_out),
                nn.ReLU(inplace=True),
            )

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            return self.net(x)

    class UNet3D(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            c1 = base_channels
            c2 = base_channels * 2
            c3 = base_channels * 4
            c4 = base_channels * 8

            self.enc1 = ConvBlock(in_channels, c1)
            self.pool1 = nn.MaxPool3d(2)
            self.enc2 = ConvBlock(c1, c2)
            self.pool2 = nn.MaxPool3d(2)
            self.enc3 = ConvBlock(c2, c3)
            self.pool3 = nn.MaxPool3d(2)
            self.enc4 = ConvBlock(c3, c4)

            self.up3 = nn.ConvTranspose3d(c4, c3, kernel_size=2, stride=2)
            self.dec3 = ConvBlock(c3 + c3, c3)
            self.up2 = nn.ConvTranspose3d(c3, c2, kernel_size=2, stride=2)
            self.dec2 = ConvBlock(c2 + c2, c2)
            self.up1 = nn.ConvTranspose3d(c2, c1, kernel_size=2, stride=2)
            self.dec1 = ConvBlock(c1 + c1, c1)
            self.head = nn.Conv3d(c1, num_classes, kernel_size=1)

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            e1 = self.enc1(x)
            e2 = self.enc2(self.pool1(e1))
            e3 = self.enc3(self.pool2(e2))
            e4 = self.enc4(self.pool3(e3))

            d3 = self.up3(e4)
            d3 = self.dec3(torch.cat([d3, e3], dim=1))
            d2 = self.up2(d3)
            d2 = self.dec2(torch.cat([d2, e2], dim=1))
            d1 = self.up1(d2)
            d1 = self.dec1(torch.cat([d1, e1], dim=1))
            return self.head(d1)

    return UNet3D()


def make_res_unet3d(
    *,
    in_channels: int,
    num_classes: int,
    base_channels: int = 24,
) -> object:
    torch, nn = _torch_import()

    def make_norm(channels: int) -> object:
        groups = min(8, int(channels))
        while groups > 1 and channels % groups != 0:
            groups -= 1
        return nn.GroupNorm(groups, channels)

    class ResidualConvBlock(nn.Module):
        def __init__(self, c_in: int, c_out: int) -> None:
            super().__init__()
            self.main = nn.Sequential(
                nn.Conv3d(c_in, c_out, kernel_size=3, padding=1, bias=False),
                make_norm(c_out),
                nn.ReLU(inplace=True),
                nn.Conv3d(c_out, c_out, kernel_size=3, padding=1, bias=False),
                make_norm(c_out),
            )
            self.skip = nn.Identity() if c_in == c_out else nn.Conv3d(c_in, c_out, kernel_size=1, bias=False)
            self.out = nn.ReLU(inplace=True)

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            return self.out(self.main(x) + self.skip(x))

    class ResidualUNet3D(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            c1 = base_channels
            c2 = base_channels * 2
            c3 = base_channels * 4
            c4 = base_channels * 8

            self.enc1 = ResidualConvBlock(in_channels, c1)
            self.pool1 = nn.MaxPool3d(2)
            self.enc2 = ResidualConvBlock(c1, c2)
            self.pool2 = nn.MaxPool3d(2)
            self.enc3 = ResidualConvBlock(c2, c3)
            self.pool3 = nn.MaxPool3d(2)
            self.enc4 = ResidualConvBlock(c3, c4)

            self.up3 = nn.ConvTranspose3d(c4, c3, kernel_size=2, stride=2)
            self.dec3 = ResidualConvBlock(c3 + c3, c3)
            self.up2 = nn.ConvTranspose3d(c3, c2, kernel_size=2, stride=2)
            self.dec2 = ResidualConvBlock(c2 + c2, c2)
            self.up1 = nn.ConvTranspose3d(c2, c1, kernel_size=2, stride=2)
            self.dec1 = ResidualConvBlock(c1 + c1, c1)
            self.head = nn.Conv3d(c1, num_classes, kernel_size=1)

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            e1 = self.enc1(x)
            e2 = self.enc2(self.pool1(e1))
            e3 = self.enc3(self.pool2(e2))
            e4 = self.enc4(self.pool3(e3))

            d3 = self.up3(e4)
            d3 = self.dec3(torch.cat([d3, e3], dim=1))
            d2 = self.up2(d3)
            d2 = self.dec2(torch.cat([d2, e2], dim=1))
            d1 = self.up1(d2)
            d1 = self.dec1(torch.cat([d1, e1], dim=1))
            return self.head(d1)

    return ResidualUNet3D()


def make_model(
    *,
    architecture: object = None,
    in_channels: int,
    num_classes: int,
    base_channels: int = 24,
    model_config: object = None,
) -> object:
    _ = model_config
    resolved_architecture = normalize_model_architecture(architecture)
    if resolved_architecture == DEFAULT_MODEL_ARCHITECTURE:
        return make_unet3d(
            in_channels=in_channels,
            num_classes=num_classes,
            base_channels=base_channels,
        )
    if resolved_architecture == RESIDUAL_UNET3D_ARCHITECTURE:
        return make_res_unet3d(
            in_channels=in_channels,
            num_classes=num_classes,
            base_channels=base_channels,
        )
    raise AssertionError(f"Unhandled model architecture: {resolved_architecture}")
