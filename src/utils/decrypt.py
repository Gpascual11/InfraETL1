import sys
from pathlib import Path
from cryptography.fernet import Fernet


def decrypt_file(key_path, file_path):
    """
    Decrypts a .csv.enc file using a .key file.
    """
    key_p = Path(key_path)
    file_p = Path(file_path)

    if not key_p.exists():
        print(f"Error: Key file not found at {key_p}")
        return

    with open(key_p, "rb") as f:
        key = f.read()

    try:
        fernet = Fernet(key)
    except Exception as e:
        print(f"Error: Invalid key. {e}")
        return

    if not file_p.exists():
        print(f"Error: Encrypted file not found at {file_p}")
        return

    with open(file_p, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)

        output_name = file_p.name.replace(".csv.enc", "_DECRYPTED.csv")
        output_path = file_p.parent / output_name

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(decrypted_data.decode('utf-8'))

        print(f"Success! Decrypted file saved to:\n{output_path}")

    except Exception as e:
        print(f"Error: Decryption failed. The key may be incorrect or the file corrupted.")
        print(f"Details: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python decrypt.py <path_to_key_file> <path_to_encrypted_file>")
        print(
            "Example: python decrypt.py output/2025_11_04.../encryption_key.key output/2025_11_04.../valid_users.csv.enc")
        sys.exit(1)

    key_path_arg = sys.argv[1]
    file_path_arg = sys.argv[2]

    decrypt_file(key_path_arg, file_path_arg)