"""
Ghostbit - A Python library for image steganography using LSB encoding.

This library provides functions for encoding and decoding secret messages
in images using Least Significant Bit (LSB) steganography.
"""

from .steganography import (
    encode_lsb,
    decode_lsb,
    encode_dct,
    decode_dct,
    calculate_psnr,
    detect_hidden_data,
)

__version__ = "0.1.0"
__all__ = [
    # Steganography functions
    "encode_lsb",
    "decode_lsb",
    "encode_dct",
    "decode_dct",
    "calculate_psnr",
    "detect_hidden_data",
]
