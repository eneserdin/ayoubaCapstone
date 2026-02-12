from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad   

# Server Configuration
PORT = 12000

def rsa_encrypt(plaintext, public_key):
    # public_key is bytes, importKey works with both PyCrypto and PyCryptodome
    cipher_rsa = PKCS1_OAEP.new(RSA.importKey(public_key))
    return cipher_rsa.encrypt(plaintext)

def aes_encrypt(plaintext, key):
    cipher_aes = AES.new(key, AES.MODE_CBC)
    iv = cipher_aes.iv

# Pad the plaintext to AES block size (16 bytes)
    padded = pad(plaintext.encode(), AES.block_size)
    ciphertext = cipher_aes.encrypt(padded)
    return iv + ciphertext

def aes_decrypt(ciphertext, key):
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]
    cipher_aes = AES.new(key, AES.MODE_CBC, iv)
    # Decrypt and unpad
    decrypted = unpad(cipher_aes.decrypt(ciphertext), AES.block_size)
    return decrypted.decode()

def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen(1)
    print("Server listening on port", PORT)

    while True:
        client_socket, addr = server_socket.accept()
        print("Connection from", addr)

        try:
            # Receive client's public key (as bytes, NOT decoded)
            client_public_key = client_socket.recv(4096)   # <-- no .decode()
            print("Received client public key")

            # Generate random AES session key (16 bytes for AES-128)
            session_key = get_random_bytes(16)

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

                    # Decrypt message using AES with padding
                    decrypted_message = aes_decrypt(data, session_key)
                    try:
                        light_value = int(decrypted_message.strip())
                        print(f"Received light value: {light_value}")

                        # Response logic (threshold 180 matches client expectation)
                        if light_value <= 180:
                            response = "ON"
                        else:
                            response = "OFF"

                        # Encrypt response using AES with padding
                        encrypted_response = aes_encrypt(response, session_key)
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
