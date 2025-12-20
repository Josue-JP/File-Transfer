from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
import datetime
import ipaddress

PASSPHRASE = "passphrase"

COUNTRY = "US"
STATE_OR_PROVINCE_NAME = "California"
LOCALITY_NAME = "San Francisco"
ORGANIZATION_NAME = "Random Comapny"
COMMON_NAME = "Socket Server"

SAN_DNS_NAMES = ["localhost"]
SAN_IP_ADDRESSES = ["127.0.0.1", "100.79.213.1", "100.82.253.38"]

key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
#print(key) == PRIVATE KEY
#print(key.public_key()) == PUBLIC KEY
# Write our key to disk for safe keeping
with open("tls_info/key.pem", "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(PASSPHRASE.encode()),
    ))


# Various details about who we are. For a self-signed certificate the
# subject and issuer are always the same.
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, COUNTRY),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, STATE_OR_PROVINCE_NAME),
    x509.NameAttribute(NameOID.LOCALITY_NAME, LOCALITY_NAME),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, ORGANIZATION_NAME),
    x509.NameAttribute(NameOID.COMMON_NAME, COMMON_NAME),
])

san_list = []
for dns in SAN_DNS_NAMES:
    san_list.append(x509.DNSName(dns))
for ip in SAN_IP_ADDRESSES:
    san_list.append(x509.IPAddress(ipaddress.IPv4Address(ip))) # The ipaddress api is needed to convert the address into a compatible format. (The address cannot be a string)

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.now(datetime.timezone.utc)
).not_valid_after(
    # The certificate will be valid for 10 days
    datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)
).add_extension(
    # This is an optional SAN
    x509.SubjectAlternativeName(san_list),
    critical=False,
# Sign our certificate with our private key
).sign(key, hashes.SHA256())
with open("tls_info/certificate.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

