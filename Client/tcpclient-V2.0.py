import RPi.GPIO as GPIO
import ADC0834
from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import HKDF
from time import sleep
import hmac
import hashlib

# GPIO setup
GPIO.setmode(GPIO.BCM)
ADC0834.setup()
GPIO.setup(22, GPIO.OUT)

# Configuration
HOST = '10.8.0.5'
PORT = 12000

def generate_rsa_key_pair():
    key = RSA.generate(2048)
    private_key = key.exportKey()
    public_key = key.publickey().exportKey()
    return private_key, public_key

def rsa_decrypt(ciphertext, private_key):
    cipher_rsa = PKCS1_OAEP.new(RSA.importKey(private_key))
    return cipher_rsa.decrypt(ciphertext)

def derive_keys(session_key):
    # Derive encryption key (16 bytes) and MAC key (32 bytes) using HKDF
    enc_key = HKDF(session_key, 16, b'enc', hashlib.sha256)
    mac_key = HKDF(session_key, 32, b'mac', hashlib.sha256)
    return enc_key, mac_key

def aes_encrypt_with_mac(plaintext, enc_key, mac_key):
    # CBC encryption with IV
    iv = get_random_bytes(16)
    cipher = AES.new(enc_key, AES.MODE_CBC, iv)
    padded = pad(plaintext.encode(), AES.block_size)
    ciphertext = cipher.encrypt(padded)

    # Compute HMAC over IV + ciphertext
    mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()

    # Return IV + ciphertext + MAC
    return iv + ciphertext + mac

def aes_decrypt_with_mac(data, enc_key, mac_key):
    # Split data: IV (16) + ciphertext (variable) + MAC (32)
    if len(data) < 16 + 32:
        raise ValueError("Data too short")
    iv = data[:16]
    mac = data[-32:]
    ciphertext = data[16:-32]

    # Verify MAC first
    computed_mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(computed_mac, mac):
        raise ValueError("MAC verification failed")

    # Decrypt and unpad
    cipher = AES.new(enc_key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()

def main():
    private_key, public_key = generate_rsa_key_pair()
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    try:
        client_socket.send(public_key)
        print("Sent public key to server")

        encrypted_session_key = client_socket.recv(2048)
        session_key = rsa_decrypt(encrypted_session_key, private_key)
        print("Secure session established (session key received)")

        # Derive encryption and MAC keys from session key
        enc_key, mac_key = derive_keys(session_key)

        while True:
            try:
                light_value = ADC0834.getResult(0)
                encrypted_message = aes_encrypt_with_mac(str(light_value), enc_key, mac_key)
                client_socket.send(encrypted_message)

                encrypted_response = client_socket.recv(2048)
                if not encrypted_response:
                    break
                response = aes_decrypt_with_mac(encrypted_response, enc_key, mac_key)

                if response.lower() == "on":
                    GPIO.output(22, True)
                    print(f"Room too dark! (Value: {light_value}) Firing up the Red LED")
                else:
                    GPIO.output(22, False)
                    print(f"Enough light! (Value: {light_value}) Red LED off!!!")

                sleep(3)

            except Exception as e:
                print(f"Error in loop: {str(e)}")
                break

    except Exception as e:
        print(f"Connection error: {str(e)}")
    finally:
        GPIO.cleanup()
        client_socket.close()
        print("Disconnected from server")

if __name__ == "__main__":
    main()