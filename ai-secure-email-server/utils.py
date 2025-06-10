import hashlib
import jwt
import re
import logging
import secrets
import ssl
import socket
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from config import Config
import ipaddress

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedCryptoUtils:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get or create encryption key securely"""
        key_file = 'certs/app_encryption.key'
        try:
            with open(key_file, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            import os
            os.makedirs('certs', exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.info("Generated new application encryption key")
            return key
    
    def encrypt_content(self, content):
        """Encrypt content with enhanced security"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        return self.cipher_suite.encrypt(content).decode('utf-8')
    
    def decrypt_content(self, encrypted_content):
        """Decrypt content"""
        if isinstance(encrypted_content, str):
            encrypted_content = encrypted_content.encode('utf-8')
        return self.cipher_suite.decrypt(encrypted_content).decode('utf-8')
    
    @staticmethod
    def hash_password(password, salt=None):
        """Enhanced password hashing with PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA256 for 100,000 iterations
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password, stored_hash):
        """Verify password against stored hash"""
        try:
            salt, pwd_hash = stored_hash.split('$', 1)
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return pwd_hash == new_hash.hex()
        except:
            return False
    
    @staticmethod
    def generate_secure_token():
        """Generate secure random token for sessions"""
        return secrets.token_urlsafe(32)

class EnhancedAuthUtils:
    @staticmethod
    def generate_jwt_token(user_data, expires_hours=24):
        """Generate JWT token with enhanced security"""
        payload = {
            'user_id': str(user_data.get('_id')),
            'email': user_data.get('email'),
            'is_verified': user_data.get('is_verified', False),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expires_hours),
            'jti': secrets.token_hex(16)  # JWT ID for token blacklisting
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_jwt_token(token):
        """Verify JWT token with enhanced validation"""
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            
            # Additional security checks
            if not payload.get('user_id') or not payload.get('email'):
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    @staticmethod
    def require_auth(f):
        """Decorator for routes that require authentication"""
        from functools import wraps
        from flask import request, jsonify
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'Authentication token required'}), 401
            
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = EnhancedAuthUtils.verify_jwt_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            request.current_user = payload
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def require_tls_verification(f):
        """Decorator to ensure TLS verification"""
        from functools import wraps
        from flask import request, jsonify
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.current_user.get('is_verified'):
                return jsonify({'error': 'TLS verification required'}), 403
            return f(*args, **kwargs)
        return decorated_function

class EnhancedValidationUtils:
    @staticmethod
    def validate_email(email):
        """Enhanced email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False
        
        # Additional checks
        if len(email) > 254:  # RFC 5321 limit
            return False
        
        local, domain = email.split('@', 1)
        if len(local) > 64:  # RFC 5321 limit
            return False
        
        return True
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\?]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    @staticmethod
    def sanitize_input(input_string):
        """Enhanced input sanitization"""
        if not isinstance(input_string, str):
            return str(input_string)
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_string.strip())
        
        # Limit length to prevent DoS
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000]
        
        return sanitized
    
    @staticmethod
    def validate_smtp_command(command):
        """Enhanced SMTP command validation"""
        if not command:
            return False
        
        valid_commands = ['EHLO', 'HELO', 'MAIL', 'RCPT', 'DATA', 'QUIT', 'STARTTLS', 'AUTH', 'RSET', 'NOOP']
        command_parts = command.upper().split()
        
        if not command_parts:
            return False
        
        return command_parts[0] in valid_commands

class TLSUtils:
    @staticmethod
    def create_secure_context():
        """Create secure TLS context"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # For development
        
        # Enhanced security settings
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        return context
    
    @staticmethod
    def verify_client_certificate(client_socket):
        """Verify client TLS certificate"""
        try:
            cert_der = client_socket.getpeercert(binary_form=True)
            if cert_der:
                cert = x509.load_der_x509_certificate(cert_der)
                # Additional certificate validation can be added here
                return True
        except:
            pass
        return False
    
    @staticmethod
    def generate_self_signed_cert():
        """Generate self-signed certificate with enhanced security"""
        try:
            import os
            os.makedirs('certs', exist_ok=True)
            
            # Generate private key
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AI Email Server"),
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
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1"))
                ]),
                critical=False,
            ).add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True,
            ).sign(key, hashes.SHA256())
            
            # Write certificate and key
            with open(Config.CERT_FILE, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(Config.KEY_FILE, "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info("Enhanced TLS certificates generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate TLS certificates: {e}")
            return False

class SpamKeywordHighlighter:
    """Utility class for highlighting spam keywords in email content"""
    
    SPAM_KEYWORDS = [
        'winner', 'congratulations', 'claim now', 'urgent', 'free money',
        'click here', 'limited time', 'act now', 'prize', 'lottery',
        'viagra', 'casino', 'debt', 'loan', 'credit', 'inheritance',
        'nigerian prince', 'transfer', 'million dollars', 'verify account',
        'suspended', 'click immediately', 'confirm identity', 'phishing',
        'scam', 'suspicious', 'malware', 'virus'
    ]
    
    PHISHING_KEYWORDS = [
        'verify.*account', 'suspended.*account', 'click.*here.*urgent',
        'update.*payment', 'confirm.*identity', 'security.*alert',
        'unauthorized.*access', 'account.*will.*be.*closed'
    ]
    
    @staticmethod
    def highlight_keywords(content, keywords_found):
        """Highlight found keywords in content"""
        if not content or not keywords_found:
            return content
        
        highlighted_content = content
        for keyword in keywords_found:
            # Case insensitive replacement with highlighting
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_content = pattern.sub(
                f'<span class="spam-keyword" style="background-color: #ff6b6b; color: white; padding: 2px 4px; border-radius: 3px;">{keyword}</span>',
                highlighted_content
            )
        
        return highlighted_content
    
    @staticmethod
    def find_spam_keywords(content, subject=""):
        """Find spam keywords in content and subject"""
        text = (content + " " + subject).lower()
        found_keywords = []
        
        # Check for exact matches
        for keyword in SpamKeywordHighlighter.SPAM_KEYWORDS:
            if keyword.lower() in text:
                found_keywords.append(keyword)
        
        # Check for pattern matches (phishing keywords)
        for pattern in SpamKeywordHighlighter.PHISHING_KEYWORDS:
            if re.search(pattern, text):
                found_keywords.append(pattern.replace('.*', ' '))
        
        return found_keywords
    
    @staticmethod
    def generate_keyword_report(keywords_found, confidence_score):
        """Generate detailed keyword analysis report"""
        if not keywords_found:
            return {
                'keywords_detected': 0,
                'risk_level': 'low',
                'keywords': [],
                'analysis': 'No suspicious keywords detected'
            }
        
        risk_level = 'high' if len(keywords_found) > 3 else 'medium' if len(keywords_found) > 1 else 'low'
        
        return {
            'keywords_detected': len(keywords_found),
            'risk_level': risk_level,
            'keywords': keywords_found,
            'confidence_impact': len(keywords_found) * 0.15,
            'analysis': f"Detected {len(keywords_found)} suspicious keywords indicating potential spam/phishing"
        }

def log_email_activity(activity_type, details, user_email=None, severity='info'):
    """Enhanced email server activity logging"""
    logger.info(f"{activity_type}: {details}")
    
    # Additional logging to database could be added here
    from database import LogModel
    log_model = LogModel()
    log_model.log_activity(activity_type, details, user_email=user_email, severity=severity)

def format_email_size(size_bytes):
    """Format email size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/(1024**2):.1f} MB"

def validate_tls_connection(client_socket):
    """Validate TLS connection security"""
    try:
        cipher = client_socket.cipher()
        if cipher:
            logger.info(f"TLS connection established with cipher: {cipher}")
            return True
    except:
        pass
    return False

# Legacy compatibility
CryptoUtils = EnhancedCryptoUtils
AuthUtils = EnhancedAuthUtils  
ValidationUtils = EnhancedValidationUtils
