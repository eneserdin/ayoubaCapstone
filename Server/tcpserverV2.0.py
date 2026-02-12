from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes

# Server Configuration
PORT = 12000

def rsa_encrypt(plaintext, public_key):
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(public_key))
    return cipher_rsa.encrypt(plaintext)

def aes_encrypt(plaintext, key):
    cipher_aes = AES.new(key, AES.MODE_CBC)
    iv = cipher_aes.iv
    ciphertext = cipher_aes.encrypt(plaintext.encode())
    return iv + ciphertext

def aes_decrypt(ciphertext, key):
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]
    cipher_aes = AES.new(key, AES.MODE_CBC, iv)
    return cipher_aes.decrypt(ciphertext).decode()

def main():
    # Create socket
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen(1)
    print("Server listening on port", PORT)

    while True:
        client_socket, addr = server_socket.accept()
        print("Connection from", addr)

        try:
            # Receive client's public key
            client_public_key = client_socket.recv(4096).decode()
            print("Received client public key")

            # Generate a random session key (AES key)
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

                    decrypted_message = aes_decrypt(data, session_key)
                    try:
                        light_value = int(decrypted_message.strip())
                        print(f"Received light value: {light_value}")

                        if light_value <= 180:
                            response = "ON" 
                        else: 
                            response = "OFF"

                        encrypted_response = aes_encrypt(response, session_key)
                        client_socket.send(encrypted_response)
                        print(f"Sent response: {response}")

                    except ValueError:
                        print("Invalid light value format")
                        break

                except Exception as e:
                    print(f"Error: {str(e)}")
                    break

        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            client_socket.close()
            print("Disconnected from client")

if __name__ == "__main__":
    main()