import cv2
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import numpy as np

class ImageSteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography - Encrypt & Decrypt")
        self.root.geometry("800x500")
        self.root.configure(bg='black')

        self.img_path = "my_stenopic.jpg"
        self.encrypted_img_path = "encrypted_image.png"
        self.key = b'Sixteen byte key'  # AES requires a 16, 24, or 32-byte key

        # Frames
        self.left_frame = tk.Frame(root, width=400, height=500, bg='black')
        self.right_frame = tk.Frame(root, width=400, height=500, bg='black')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Title Labels
        self.enc_label = tk.Label(self.left_frame, text="Encryption", fg='lime', bg='black', font=("Courier", 16, "bold"))
        self.dec_label = tk.Label(self.right_frame, text="Decryption", fg='lime', bg='black', font=("Courier", 16, "bold"))
        self.enc_label.pack(pady=10)
        self.dec_label.pack(pady=10)

        # Encryption Inputs
        self.msg_label = tk.Label(self.left_frame, text="Secret Message:", fg='lime', bg='black', font=("Courier", 12))
        self.msg_entry = tk.Entry(self.left_frame, width=40, bg='black', fg='lime', insertbackground='lime', font=("Courier", 12))
        self.pass_label = tk.Label(self.left_frame, text="Passcode:", fg='lime', bg='black', font=("Courier", 12))
        self.pass_entry = tk.Entry(self.left_frame, show='*', width=40, bg='black', fg='lime', insertbackground='lime', font=("Courier", 12))
        self.encrypt_btn = tk.Button(self.left_frame, text="Encrypt", command=self.encrypt_message, bg='black', fg='lime', font=("Courier", 12))

        self.msg_label.pack()
        self.msg_entry.pack()
        self.pass_label.pack()
        self.pass_entry.pack()
        self.encrypt_btn.pack(pady=10)

        # Decryption Inputs
        self.pass_label_dec = tk.Label(self.right_frame, text="Passcode:", fg='lime', bg='black', font=("Courier", 12))
        self.pass_entry_dec = tk.Entry(self.right_frame, show='*', width=40, bg='black', fg='lime', insertbackground='lime', font=("Courier", 12))
        self.decrypt_btn = tk.Button(self.right_frame, text="Decrypt", command=self.decrypt_message, bg='black', fg='lime', font=("Courier", 12))
        self.output_label = tk.Label(self.right_frame, text="Decrypted Message:", fg='lime', bg='black', font=("Courier", 12))
        self.output_text = tk.Label(self.right_frame, text="", fg='lime', bg='black', font=("Courier", 14, "bold"), wraplength=380)

        self.pass_label_dec.pack()
        self.pass_entry_dec.pack()
        self.decrypt_btn.pack()
        self.output_label.pack()
        self.output_text.pack()

    def encrypt_message(self):
        msg = self.msg_entry.get()
        password = self.pass_entry.get()

        if not msg or not password:
            messagebox.showerror("Error", "Message and passcode cannot be empty!")
            return

        img = cv2.imread(self.img_path)
        n, m, z = 0, 0, 0

        # Encrypt password
        encrypted_pass = base64.b64encode(AES.new(self.key, AES.MODE_ECB).encrypt(pad(password.encode(), AES.block_size))).decode()
        msg = encrypted_pass + '|' + msg + '\0'  # Append a null terminator to detect message end

        # Store message length in first pixel
        msg_length = len(msg)
        img[0, 0, 0] = msg_length

        for i in range(msg_length):
            img[n, m, z] = ord(msg[i])
            n = (n + 1) % img.shape[0]
            m = (m + 1) % img.shape[1]
            z = (z + 1) % 3

        cv2.imwrite(self.encrypted_img_path, img)
        messagebox.showinfo("Success", "Message encrypted successfully!")

    def decrypt_message(self):
        img = cv2.imread(self.encrypted_img_path)
        n, m, z = 0, 0, 0

        # Retrieve message length
        msg_length = img[0, 0, 0]

        extracted_msg = ""
        for _ in range(msg_length):
            char = chr(img[n, m, z])
            if char == '\0':  # Stop at null terminator
                break
            extracted_msg += char
            n = (n + 1) % img.shape[0]
            m = (m + 1) % img.shape[1]
            z = (z + 1) % 3

        if '|' not in extracted_msg:
            messagebox.showerror("Error", "Corrupted data! No delimiter found.")
            return

        stored_pass, message = extracted_msg.split('|', 1)
        user_pass = self.pass_entry_dec.get()

        try:
            decrypted_pass = unpad(AES.new(self.key, AES.MODE_ECB).decrypt(base64.b64decode(stored_pass)), AES.block_size).decode()
            if decrypted_pass == user_pass:
                self.output_text.config(text=message)
            else:
                messagebox.showerror("Error", "Incorrect passcode!")
        except:
            messagebox.showerror("Error", "Decryption failed. Invalid or corrupted data!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSteganographyApp(root)
    root.mainloop()
