import RPi.GPIO as GPIO
import ADC0834
from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes

# Configuration
HOST = '10.8.0.26'
PORT = 12000

def generate_rsa_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def rsa_decrypt(ciphertext, private_key):
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(private_key))
    return cipher_rsa.decrypt(ciphertext)

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
    # Generate client's own RSA key pair
    private_key, public_key = generate_rsa_key_pair()

    # Create socket
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    try:
        # Send public key to server
        client_socket.send(public_key.encode())
        print("Sent public key to server")

        # Receive encrypted session key
        encrypted_session_key = client_socket.recv(2048)
        session_key = rsa_decrypt(encrypted_session_key, private_key)
        print("Secure session established (session key received)")

        # Send light values
        while True:
            try:
                light_value = int(ADC0834.getResult(0))
                encrypted_message = aes_encrypt(str(light_value), session_key)
                client_socket.send(encrypted_message)

                # Receive and decrypt server response
                encrypted_response = client_socket.recv(2048)
                response = aes_decrypt(encrypted_response, session_key)
                print(f"Server response: {response}")

            except ValueError:
                print("Invalid Light Value")
            except Exception as e:
                print(f"Error: {str(e)}")
                break

    except Exception as e:
        print(f"Connection error: {str(e)}")
    finally:
        client_socket.close()
        print("Disconnected from server")

if __name__ == "__main__":
    main()