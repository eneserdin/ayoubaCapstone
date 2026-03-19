import RPi.GPIO as GPIO
import ADC0834
from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad  
from time import sleep

# GPIO setup
GPIO.setmode(GPIO.BCM)
ADC0834.setup()
GPIO.setup(20, GPIO.OUT)

# Configuration
HOST = '10.8.0.26'
PORT = 12000

def generate_rsa_key_pair():
    key = RSA.generate(2048)
    private_key = key.exportKey()          
    public_key = key.publickey().exportKey()
    return private_key, public_key

def rsa_decrypt(ciphertext, private_key):
    cipher_rsa = PKCS1_OAEP.new(RSA.importKey(private_key))
    return cipher_rsa.decrypt(ciphertext)

def aes_encrypt(plaintext, key):
    cipher_aes = AES.new(key, AES.MODE_CBC)
    iv = cipher_aes.iv
    # ✅ BUILT-IN PKCS7 PADDING
    ciphertext = cipher_aes.encrypt(pad(plaintext.encode(), AES.block_size))
    return iv + ciphertext

def aes_decrypt(ciphertext, key):
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]
    cipher_aes = AES.new(key, AES.MODE_CBC, iv)
    # ✅ BUILT-IN UNPADDING
    decrypted = unpad(cipher_aes.decrypt(ciphertext), AES.block_size)
    return decrypted.decode()

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

        while True:
            try:
                light_value = ADC0834.getResult(0)
                encrypted_message = aes_encrypt(str(light_value), session_key)
                client_socket.send(encrypted_message)   # ✅ direct send

                encrypted_response = client_socket.recv(2048)
                response = aes_decrypt(encrypted_response, session_key)

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
