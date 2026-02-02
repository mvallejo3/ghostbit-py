"""
Steganography implementation with LSB and DCT methods.
Supports embedding and extracting secret messages in images.
"""

from PIL import Image
import numpy as np
from scipy.fft import dct, idct


def encode_lsb(img_path, message, output_path):
    """
    Encode a message into an image using LSB (Least Significant Bit) steganography.
    
    Args:
        img_path: Path to the cover image
        message: Secret message to embed
        output_path: Path to save the stego-image
    
    Raises:
        ValueError: If the image is too small to hold the message
    """
    img = Image.open(img_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    width, height = img.size
    pixels = np.array(img)
    
    # Convert message to binary string
    message += chr(0)  # Null delimiter
    binary_message = ''.join(format(ord(c), '08b') for c in message)
    message_length = len(binary_message)
    
    # Check if image has enough capacity (3 bits per pixel)
    max_capacity = width * height * 3
    if message_length > max_capacity:
        raise ValueError(f"Message too long. Max capacity: {max_capacity} bits, "
                        f"message requires: {message_length} bits")
    
    # Embed message bits into LSBs
    bit_index = 0
    for y in range(height):
        for x in range(width):
            for channel in range(3):  # RGB channels
                if bit_index < message_length:
                    # Clear LSB and set it to message bit
                    # Use 0xFE (254) instead of ~1 to avoid signed integer issues with uint8
                    pixels[y, x, channel] = (pixels[y, x, channel] & 0xFE) | int(binary_message[bit_index])
                    bit_index += 1
                else:
                    break
            if bit_index >= message_length:
                break
        if bit_index >= message_length:
            break
    
    # Save stego-image
    stego_img = Image.fromarray(pixels)
    stego_img.save(output_path)
    # print(f"Message encoded successfully. Saved to {output_path}")


def decode_lsb(img_path):
    """
    Decode a message from an image using LSB steganography.
    
    Args:
        img_path: Path to the stego-image
    
    Returns:
        Extracted secret message
    """
    img = Image.open(img_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    width, height = img.size
    pixels = np.array(img)
    
    # Extract LSBs
    binary_message = []
    for y in range(height):
        for x in range(width):
            for channel in range(3):  # RGB channels
                # Extract LSB
                binary_message.append(str(pixels[y, x, channel] & 1))
    
    # Convert binary string to message
    message = []
    for i in range(0, len(binary_message), 8):
        byte = ''.join(binary_message[i:i+8])
        if len(byte) == 8:
            char = chr(int(byte, 2))
            if char == chr(0):  # Null delimiter found
                return ''.join(message)
            message.append(char)
    
    return ''.join(message)


def encode_dct(img_path, message, output_path, block_size=8):
    """
    Encode a message into an image using DCT (Discrete Cosine Transform) steganography.
    
    Args:
        img_path: Path to the cover image
        message: Secret message to embed
        output_path: Path to save the stego-image
        block_size: Size of DCT blocks (default: 8x8)
    
    Raises:
        ValueError: If the image is too small to hold the message
    """
    img = Image.open(img_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    width, height = img.size
    pixels = np.array(img, dtype=np.float64)
    
    # Convert message to binary string
    message += chr(0)  # Null delimiter
    binary_message = ''.join(format(ord(c), '08b') for c in message)
    message_length = len(binary_message)
    
    # Calculate capacity (using middle frequency coefficients)
    num_blocks_x = width // block_size
    num_blocks_y = height // block_size
    # Use 1 coefficient per block per channel (middle frequency position)
    max_capacity = num_blocks_x * num_blocks_y * 3
    
    if message_length > max_capacity:
        raise ValueError(f"Message too long. Max capacity: {max_capacity} bits, "
                        f"message requires: {message_length} bits")
    
    # Process each channel separately
    bit_index = 0
    for channel in range(3):
        channel_data = pixels[:, :, channel]
        
        for block_y in range(num_blocks_y):
            for block_x in range(num_blocks_x):
                if bit_index >= message_length:
                    break
                
                # Extract 8x8 block
                y_start = block_y * block_size
                y_end = y_start + block_size
                x_start = block_x * block_size
                x_end = x_start + block_size
                
                block = channel_data[y_start:y_end, x_start:x_end]
                
                # Apply DCT
                dct_block = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
                
                # Embed bit in middle frequency coefficient (position 3,3)
                embed_pos = (3, 3)
                if bit_index < message_length:
                    bit_value = int(binary_message[bit_index])
                    # Quantize and embed: if bit is 1, make quantized coefficient odd; if 0, make even
                    coeff = dct_block[embed_pos]
                    quantized = int(np.round(coeff))
                    # Adjust to match desired bit value
                    if (quantized % 2) != bit_value:
                        quantized = quantized + 1 if quantized >= 0 else quantized - 1
                    dct_block[embed_pos] = quantized
                    bit_index += 1
                
                # Apply inverse DCT
                idct_block = idct(idct(dct_block, axis=0, norm='ortho'), axis=1, norm='ortho')
                
                # Update channel data
                channel_data[y_start:y_end, x_start:x_end] = idct_block
            
            if bit_index >= message_length:
                break
        
        pixels[:, :, channel] = channel_data
    
    # Clip values to valid range and convert back to uint8
    pixels = np.clip(pixels, 0, 255).astype(np.uint8)
    
    # Save stego-image
    stego_img = Image.fromarray(pixels)
    stego_img.save(output_path)
    # print(f"Message encoded successfully using DCT. Saved to {output_path}")


def decode_dct(img_path, block_size=8):
    """
    Decode a message from an image using DCT steganography.
    
    Args:
        img_path: Path to the stego-image
        block_size: Size of DCT blocks (default: 8x8)
    
    Returns:
        Extracted secret message
    """
    img = Image.open(img_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    width, height = img.size
    pixels = np.array(img, dtype=np.float64)
    
    # Extract bits from DCT coefficients
    binary_message = []
    num_blocks_x = width // block_size
    num_blocks_y = height // block_size
    
    for channel in range(3):
        channel_data = pixels[:, :, channel]
        
        for block_y in range(num_blocks_y):
            for block_x in range(num_blocks_x):
                # Extract 8x8 block
                y_start = block_y * block_size
                y_end = y_start + block_size
                x_start = block_x * block_size
                x_end = x_start + block_size
                
                block = channel_data[y_start:y_end, x_start:x_end]
                
                # Apply DCT
                dct_block = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
                
                # Extract bit from middle frequency coefficient (position 3,3)
                embed_pos = (3, 3)
                coeff = dct_block[embed_pos]
                # Extract LSB of quantized coefficient
                bit_value = int(np.round(coeff)) % 2
                binary_message.append(str(bit_value))
    
    # Convert binary string to message
    message = []
    for i in range(0, len(binary_message), 8):
        byte = ''.join(binary_message[i:i+8])
        if len(byte) == 8:
            char = chr(int(byte, 2))
            if char == chr(0):  # Null delimiter found
                return ''.join(message)
            message.append(char)
    
    return ''.join(message)


def calculate_psnr(img1_path, img2_path):
    """
    Calculate PSNR (Peak Signal-to-Noise Ratio) between two images.
    
    Args:
        img1_path: Path to first image
        img2_path: Path to second image
    
    Returns:
        PSNR value in dB
    """
    img1 = np.array(Image.open(img1_path).convert('RGB'))
    img2 = np.array(Image.open(img2_path).convert('RGB'))
    
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr


def detect_hidden_data(img_path, method='decode'):
    """
    Detect whether an image contains hidden data using LSB steganography.
    
    Args:
        img_path: Path to the image to analyze
        method: Detection method to use:
            - 'decode': Try to decode and check for null-terminated message (fast, reliable)
            - 'statistical': Use statistical analysis of LSB distribution
            - 'both': Use both methods and return combined result
    
    Returns:
        dict with keys:
            - has_hidden_data: bool indicating if hidden data was detected
            - confidence: float between 0.0 and 1.0 indicating confidence level
            - method_used: str indicating which method(s) were used
            - decoded_message: str if decode method found a message (None otherwise)
            - message_length: int length of decoded message if found (None otherwise)
    """
    img = Image.open(img_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    width, height = img.size
    pixels = np.array(img)
    
    result = {
        'has_hidden_data': False,
        'confidence': 0.0,
        'method_used': method,
        'decoded_message': None,
        'message_length': None
    }
    
    # Method 1: Try to decode and check for null-terminated message
    if method in ('decode', 'both'):
        try:
            decoded = decode_lsb(img_path)
            if decoded:  # Found a non-empty null-terminated message
                result['has_hidden_data'] = True
                result['confidence'] = 0.95  # High confidence if decode succeeds
                result['decoded_message'] = decoded
                result['message_length'] = len(decoded)
                if method == 'decode':
                    return result
        except Exception:
            pass  # Decode failed, continue with other methods
    
    # Method 2: Statistical analysis of LSB distribution
    if method in ('statistical', 'both'):
        # Extract all LSBs
        lsbs = pixels & 1
        total_bits = width * height * 3
        
        # Count 0s and 1s in LSBs
        zeros = np.sum(lsbs == 0)
        ones = np.sum(lsbs == 1)
        
        # In natural images, LSBs should be roughly 50/50 (random)
        # If there's hidden data, we might see patterns
        # Check if distribution is significantly skewed
        expected = total_bits / 2
        if total_bits > 0:
            deviation = abs(zeros - expected) / expected
            
            # Also check for patterns: consecutive same bits might indicate data
            # Sample a subset to check for patterns
            sample_size = min(10000, total_bits)
            sample_indices = np.random.choice(total_bits, sample_size, replace=False)
            sample_lsbs = lsbs.flatten()[sample_indices]
            
            # Count transitions (0->1 or 1->0)
            transitions = np.sum(np.diff(sample_lsbs) != 0)
            transition_ratio = transitions / (sample_size - 1) if sample_size > 1 else 0
            
            # Natural images have high transition ratio (~0.5)
            # Hidden data might have lower transition ratio if it's structured
            # But this is not definitive, so we use low confidence
            
            # If deviation is very high or transition ratio is very low, might indicate data
            if deviation > 0.1 or transition_ratio < 0.3:
                if method == 'statistical':
                    result['has_hidden_data'] = True
                    result['confidence'] = 0.3  # Low confidence for statistical method
                elif method == 'both' and not result['has_hidden_data']:
                    result['has_hidden_data'] = True
                    result['confidence'] = 0.4  # Medium confidence when decode failed but stats suggest data
    
    return result
