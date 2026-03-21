from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import HKDF
import hmac
import hashlib

# Server Configuration
PORT = 12000

def rsa_encrypt(plaintext, public_key):
    cipher_rsa = PKCS1_OAEP.new(RSA.importKey(public_key))
    return cipher_rsa.encrypt(plaintext)

def derive_keys(session_key):
    # Derive encryption key (16 bytes) and MAC key (32 bytes) using HKDF
    enc_key = HKDF(session_key, 16, b'enc', hashlib.sha256)
    mac_key = HKDF(session_key, 32, b'mac', hashlib.sha256)
    return enc_key, mac_key

def aes_encrypt_with_mac(plaintext, enc_key, mac_key):
    iv = get_random_bytes(16)
    cipher = AES.new(enc_key, AES.MODE_CBC, iv)
    padded = pad(plaintext.encode(), AES.block_size)
    ciphertext = cipher.encrypt(padded)

    mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()
    return iv + ciphertext + mac

def aes_decrypt_with_mac(data, enc_key, mac_key):
    if len(data) < 16 + 32:
        raise ValueError("Data too short")
    iv = data[:16]
    mac = data[-32:]
    ciphertext = data[16:-32]

    computed_mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(computed_mac, mac):
        raise ValueError("MAC verification failed")

    cipher = AES.new(enc_key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()

def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen(1)
    print("Server listening on port", PORT)

    while True:
        client_socket, addr = server_socket.accept()
        print("Connection from", addr)

        try:
            # Receive client's public key
            client_public_key = client_socket.recv(4096)
            print("Received client public key")

            # Generate random AES session key (16 bytes for AES-128)
            session_key = get_random_bytes(16)

            # Derive encryption and MAC keys from session key
            enc_key, mac_key = derive_keys(session_key)

            # Encrypt session key with client's public key
            encrypted_session_key = rsa_encrypt(session_key, client_public_key)
            client_socket.send(encrypted_session_key)
            print("Session key sent to client")

            # Handle client communication
            while True:
                try:
                    data = client_socket.recv(2048)
                    if not data:
                        break

                    # Decrypt message (MAC is verified inside)
                    decrypted_message = aes_decrypt_with_mac(data, enc_key, mac_key)
                    try:
                        light_value = int(decrypted_message.strip())
                        print(f"Received light value: {light_value}")

                        # Response logic
                        if light_value <= 180:
                            response = "ON"
                        else:
                            response = "OFF"

                        # Encrypt response with MAC
                        encrypted_response = aes_encrypt_with_mac(response, enc_key, mac_key)
                        client_socket.send(encrypted_response)
                        print(f"Sent response: {response}")

                    except ValueError:
                        print("Invalid light value format")
                        break

                except Exception as e:
                    print(f"Error in client loop: {str(e)}")
                    break

        except Exception as e:
            print(f"Error handling client: {str(e)}")
        finally:
            client_socket.close()
            print("Disconnected from client")

if __name__ == "__main__":
    main()
