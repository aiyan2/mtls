import os
import subprocess

# Create the directory structure for certificates
base_dir = os.path.expanduser('./certs/mutual-tls')  # Use the current directory
ca_dir = os.path.join(base_dir, 'ca')
server_dir = os.path.join(base_dir, 'server')
client_dir = os.path.join(base_dir, 'client')

# Create directories if they don't exist
os.makedirs(ca_dir, exist_ok=True)
os.makedirs(server_dir, exist_ok=True)
os.makedirs(client_dir, exist_ok=True)

# Paths for the files
ca_key = os.path.join(ca_dir, 'ca.key')
ca_crt = os.path.join(ca_dir, 'ca.crt')
server_key = os.path.join(server_dir, 'server.key')
server_csr = os.path.join(server_dir, 'server.csr')
server_crt = os.path.join(server_dir, 'server.crt')
client_key = os.path.join(client_dir, 'client.key')
client_csr = os.path.join(client_dir, 'client.csr')
client_crt = os.path.join(client_dir, 'client.crt')

# Step 1: Create the Certificate Authority (CA)
print("Generating CA private key...")
subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-out', ca_key, '-aes256'])

print("Generating CA certificate...")
subprocess.run(['openssl', 'req', '-key', ca_key, '-new', '-x509', '-out', ca_crt, '-days', '3650', '-subj', '/CN=MyDevCA'])

# Step 2: Create the Server Certificate
print("Generating server private key...")
subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-out', server_key])

print("Generating server CSR...")
subprocess.run(['openssl', 'req', '-new', '-key', server_key, '-out', server_csr, '-subj', '/CN=localhost'])

print("Signing server certificate with CA...")
subprocess.run(['openssl', 'x509', '-req', '-in', server_csr, '-CA', ca_crt, '-CAkey', ca_key, '-CAcreateserial', '-out', server_crt, '-days', '3650'])

# Step 3: Create the Client Certificate
print("Generating client private key...")
subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-out', client_key])

print("Generating client CSR...")
subprocess.run(['openssl', 'req', '-new', '-key', client_key, '-out', client_csr, '-subj', '/CN=client'])

print("Signing client certificate with CA...")
subprocess.run(['openssl', 'x509', '-req', '-in', client_csr, '-CA', ca_crt, '-CAkey', ca_key, '-CAcreateserial', '-out', client_crt, '-days', '3650'])

# Step 4: Output completion
print(f"\nCertificates have been generated in the following directories:")
print(f" - CA Certificate: {ca_crt}")
print(f" - Server Certificate: {server_crt}")
print(f" - Server Key: {server_key}")
print(f" - Client Certificate: {client_crt}")
print(f" - Client Key: {client_key}")

print("\nCertificates are ready for use with your mTLS server.")
