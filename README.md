# Ghostbit

A Python library for image steganography using LSB (Least Significant Bit) encoding.

## Features

- **LSB Steganography**: Encode and decode secret messages in images using the Least Significant Bit method
- **DCT Steganography**: Alternative encoding method using Discrete Cosine Transform
- **Image Analysis**: Detect hidden data and calculate image quality metrics

## Installation

```bash
pip install ghostbit
```

Or install from source:

```bash
cd ghostbit-py
pip install -e .
```

## Quick Start

```python
from ghostbit import encode_lsb, decode_lsb

# Encode a message into an image
encode_lsb("cover_image.png", "secret message", "stego_image.png")

# Decode a message from an image
message = decode_lsb("stego_image.png")
print(message)  # Output: secret message
```

## Usage Examples

### Basic Encoding/Decoding

```python
from ghostbit import encode_lsb, decode_lsb

# Encode a secret message
encode_lsb("input.png", "My secret password", "output.png")

# Decode the message
secret = decode_lsb("output.png")
```


## API Reference

### Steganography Functions

- `encode_lsb(img_path, message, output_path)` - Encode message using LSB
- `decode_lsb(img_path)` - Decode message using LSB
- `encode_dct(img_path, message, output_path, block_size=8)` - Encode using DCT
- `decode_dct(img_path, block_size=8)` - Decode using DCT
- `detect_hidden_data(img_path, method='decode')` - Detect hidden data
- `calculate_psnr(img1_path, img2_path)` - Calculate PSNR between images

## Requirements

- Python >= 3.8
- Pillow >= 10.0.0
- numpy >= 1.24.0
- scipy >= 1.10.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
