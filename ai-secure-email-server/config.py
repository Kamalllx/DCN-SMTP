import os
import ssl
import ipaddress  # Add this import
from pathlib import Path

class Config:
    # Database Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/email_server')
    
    # AI Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    # Email Server Configuration
    SMTP_PORT = 587
    IMAP_PORT = 993
    POP3_PORT = 995
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    JWT_EXPIRATION_HOURS = 24
    
    # TLS/SSL Configuration
    CERT_FILE = 'certs/server.crt'
    KEY_FILE = 'certs/server.key'
    
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True

class SecurityConfig:
    @staticmethod
    def create_ssl_context():
        """Create SSL context for secure connections"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            context.load_cert_chain(Config.CERT_FILE, Config.KEY_FILE)
        except FileNotFoundError:
            print("SSL certificates not found. Generating self-signed certificates...")
            SecurityConfig.generate_self_signed_cert()
            context.load_cert_chain(Config.CERT_FILE, Config.KEY_FILE)
        return context
    
    @staticmethod
    def generate_self_signed_cert():
        """Generate self-signed SSL certificates"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime
            
            # Create certificates directory
            Path('certs').mkdir(exist_ok=True)
            
            # Generate private key
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Email Server"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1"))  # Fixed: Use ipaddress.IPv4Address
                ]),
                critical=False,
            ).sign(key, hashes.SHA256())
            
            # Write certificate and key to files
            with open(Config.CERT_FILE, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(Config.KEY_FILE, "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            print("Self-signed certificates generated successfully!")
            
        except ImportError as e:
            print(f"Warning: Could not generate SSL certificates. Missing dependency: {e}")
            print("Install cryptography: pip install cryptography")
            # Create dummy certificates for development
            SecurityConfig._create_dummy_certs()
        except Exception as e:
            print(f"Error generating SSL certificates: {e}")
            # Create dummy certificates for development  
            SecurityConfig._create_dummy_certs()
    
    @staticmethod
    def _create_dummy_certs():
        """Create dummy certificate files for development"""
        Path('certs').mkdir(exist_ok=True)
        
        # Create dummy cert file
        with open(Config.CERT_FILE, "w") as f:
            f.write("-----BEGIN CERTIFICATE-----\nDUMMY CERTIFICATE FOR DEVELOPMENT\n-----END CERTIFICATE-----\n")
        
        # Create dummy key file
        with open(Config.KEY_FILE, "w") as f:
            f.write("-----BEGIN PRIVATE KEY-----\nDUMMY PRIVATE KEY FOR DEVELOPMENT\n-----END PRIVATE KEY-----\n")
        
        print("Warning: Using dummy certificates for development only!")
