from flask import Flask, request, send_file, render_template
from cryptography.fernet import Fernet
import boto3
import os

app = Flask(__name__)

# Generate and store a key for encryption
def generate_key():
    return Fernet.generate_key()

# Encrypt file
@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    file = request.files['file']
    key = generate_key()
    cipher = Fernet(key)
    
    # Encrypt file data
    file_data = file.read()
    encrypted_data = cipher.encrypt(file_data)
    
    # Save encrypted file
    with open('encrypted_file', 'wb') as enc_file:
        enc_file.write(encrypted_data)
    
    return send_file('encrypted_file', as_attachment=True, download_name='encrypted_file')

# Decrypt file
@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    file = request.files['file']
    encryption_key = request.form['encryption_key'].encode()
    cipher = Fernet(encryption_key)
    
    # Decrypt file data
    file_data = file.read()
    decrypted_data = cipher.decrypt(file_data)
    
    # Save decrypted file
    with open('decrypted_file', 'wb') as dec_file:
        dec_file.write(decrypted_data)
    
    return send_file('decrypted_file', as_attachment=True, download_name='decrypted_file')

# Upload to AWS S3
@app.route('/upload', methods=['POST'])
def upload_to_s3():
    file = request.files['file']
    aws_access_key = request.form['aws_access_key']
    aws_secret_key = request.form['aws_secret_key']
    bucket_name = request.form['bucket_name']
    
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    s3.upload_fileobj(file, bucket_name, file.filename)
    
    return "File uploaded successfully!"

# Download from AWS S3
@app.route('/download', methods=['POST'])
def download_from_s3():
    aws_access_key = request.form['aws_access_key']
    aws_secret_key = request.form['aws_secret_key']
    bucket_name = request.form['bucket_name']
    filename = request.form['filename']
    
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    s3.download_file(bucket_name, filename, filename)
    
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
