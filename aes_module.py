import base64
import hashlib
from Crypto.Cipher import AES  # type: ignore
from Crypto.Util.Padding import pad, unpad  # type: ignore
from PIL import Image  # type: ignore
import numpy as np  # type: ignore

def derive_key(user_input: str) -> bytes:
    return hashlib.sha256(user_input.encode()).digest()[:16]

def encrypt_neqr(neqr_data, key: bytes, save_path: str):
    bit_string = ''.join(r + g + b + pos for (r, g, b, pos) in neqr_data)
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(bit_string.encode(), AES.block_size))
    ciphertext_b64 = base64.b64encode(ciphertext).decode()

    with open(save_path, "w") as f:
        f.write(ciphertext_b64)

    print(f"\nEncrypted NEQR saved to: {save_path}")
    return ciphertext_b64


def decrypt_neqr(ciphertext_b64: str, key: bytes):
    ciphertext = base64.b64decode(ciphertext_b64)
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    binary_str = plaintext.decode()

    pixels = []
    
    for i in range(0, len(binary_str), 28):
        r_bin = binary_str[i:i+8]
        g_bin = binary_str[i+8:i+16]
        b_bin = binary_str[i+16:i+24]
        

        r_val = int(r_bin, 2)
        g_val = int(g_bin, 2)
        b_val = int(b_bin, 2)
        pixels.append((r_val, g_val, b_val))

    return pixels

def reconstruct_image(pixel_vals, size=(4, 4)):
    arr = np.array(pixel_vals).reshape((size[0], size[1], 3))
    img = Image.fromarray(arr.astype(np.uint8), 'RGB')
    return img

