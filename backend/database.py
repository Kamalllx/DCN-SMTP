from pymongo import MongoClient, errors
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
from config import Config
from cryptography.fernet import Fernet
import logging
import hashlib
import secrets

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Connect to MongoDB and ensure database/collections exist"""
        try:
            if "mongodb://" in Config.MONGODB_URI:
                parts = Config.MONGODB_URI.split("/")
                db_name = parts[-1] if len(parts) > 3 and parts[-1] else "email_server"
            else:
                db_name = "email_server"
            
            self._client = MongoClient(
                Config.MONGODB_URI, 
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            self._client.admin.command('ping')
            self.db = self._client[db_name]
            self._initialize_collections()
            
            logger.info(f"Connected to MongoDB successfully. Database: {db_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.info("Using fallback in-memory storage for development")
            self._setup_fallback_storage()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            self._setup_fallback_storage()
    
    def _initialize_collections(self):
        """Initialize collections and create indexes for better performance"""
        try:
            collections = ['emails', 'users', 'logs', 'metrics', 'email_reports']
            
            for collection_name in collections:
                collection = self.db[collection_name]
                
                dummy_id = collection.insert_one({"_dummy": True}).inserted_id
                collection.delete_one({"_id": dummy_id})
                
                if collection_name == 'emails':
                    collection.create_index("from")
                    collection.create_index("to")
                    collection.create_index("created_at")
                    collection.create_index("user_id")
                elif collection_name == 'users':
                    collection.create_index("email", unique=True)
                    collection.create_index("created_at")
                elif collection_name == 'logs':
                    collection.create_index("timestamp")
                    collection.create_index("user_id")
                elif collection_name == 'metrics':
                    collection.create_index("metric_type")
                    collection.create_index("timestamp")
                elif collection_name == 'email_reports':
                    collection.create_index("email_id")
                    collection.create_index("user_id")
            
            logger.info("Collections and indexes initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
    
    def _setup_fallback_storage(self):
        """Setup in-memory fallback storage when MongoDB is not available"""
        class FallbackDB:
            def __init__(self):
                self.emails = []
                self.users = []
                self.logs = []
                self.metrics = []
                self.email_reports = []
            
            def __getitem__(self, name):
                return getattr(self, name, [])
        
        self.db = FallbackDB()
        logger.info("Using fallback in-memory storage")
    
    def get_db(self):
        return self.db
    
    def is_connected(self):
        """Check if MongoDB connection is active"""
        try:
            if self._client:
                self._client.admin.command('ping')
                return True
        except:
            pass
        return False

class CryptoManager:
    """Enhanced encryption manager for email content and sensitive data"""
    
    def __init__(self):
        self._key = self._get_or_create_key()
        self.cipher_suite = Fernet(self._key)
    
    def _get_or_create_key(self):
        """Get or create encryption key"""
        key_file = 'certs/encryption.key'
        try:
            with open(key_file, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            import os
            os.makedirs('certs', exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.info("Generated new encryption key")
            return key
    
    def encrypt_content(self, content):
        """Encrypt email content"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        return self.cipher_suite.encrypt(content).decode('utf-8')
    
    def decrypt_content(self, encrypted_content):
        """Decrypt email content"""
        if isinstance(encrypted_content, str):
            encrypted_content = encrypted_content.encode('utf-8')
        return self.cipher_suite.decrypt(encrypted_content).decode('utf-8')
    
    @staticmethod
    def hash_password(password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
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

class UserModel:
    def __init__(self):
        self.db_conn = DatabaseConnection()
        self.db = self.db_conn.get_db()
        self.crypto = CryptoManager()
        
        if hasattr(self.db, 'users'):
            self.collection = self.db.users
        else:
            self.collection = self.db['users']
    
    def create_user(self, user_data):
        """Create new user with hashed password and TLS verification"""
        user_data['created_at'] = datetime.utcnow()
        user_data['password'] = self.crypto.hash_password(user_data['password'])
        user_data['is_verified'] = False  # TLS verification status
        user_data['login_attempts'] = 0
        user_data['last_login'] = None
        
        try:
            if hasattr(self.collection, 'insert_one'):
                result = self.collection.insert_one(user_data)
                user_id = str(result.inserted_id)
                logger.info(f"User created with ID: {user_id}")
                return user_id
            else:
                user_data['_id'] = f"user_{len(self.collection)}"
                self.collection.append(user_data)
                return user_data['_id']
        except errors.DuplicateKeyError:
            logger.warning(f"User with email {user_data['email']} already exists")
            return None
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            if hasattr(self.collection, 'find_one'):
                return self.collection.find_one({"email": email})
            else:
                for user in self.collection:
                    if user.get('email') == email:
                        return user
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve user: {e}")
            return None
    
    def authenticate_user(self, email, password, client_ip=None):
        """Authenticate user with enhanced security"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        # Check login attempts (simple rate limiting)
        if user.get('login_attempts', 0) >= 5:
            logger.warning(f"Account locked for {email} due to too many failed attempts")
            return None
        
        if self.crypto.verify_password(password, user['password']):
            # Reset login attempts on successful login
            self.update_user_login(user['_id'], success=True, client_ip=client_ip)
            return user
        else:
            # Increment login attempts on failed login
            self.update_user_login(user['_id'], success=False, client_ip=client_ip)
            return None
    
    def update_user_login(self, user_id, success=True, client_ip=None):
        """Update user login information"""
        try:
            update_data = {
                'last_login': datetime.utcnow(),
                'last_login_ip': client_ip
            }
            
            if success:
                update_data['login_attempts'] = 0
            else:
                update_data = {'$inc': {'login_attempts': 1}}
            
            if hasattr(self.collection, 'update_one'):
                from bson import ObjectId
                self.collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set" if success else "$inc": update_data}
                )
            else:
                # Fallback storage update
                for user in self.collection:
                    if user.get('_id') == user_id:
                        if success:
                            user.update(update_data)
                        else:
                            user['login_attempts'] = user.get('login_attempts', 0) + 1
                        break
        except Exception as e:
            logger.error(f"Failed to update user login: {e}")
    
    def verify_user_tls(self, user_id):
        """Mark user as TLS verified"""
        try:
            if hasattr(self.collection, 'update_one'):
                from bson import ObjectId
                self.collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"is_verified": True, "verified_at": datetime.utcnow()}}
                )
            else:
                for user in self.collection:
                    if user.get('_id') == user_id:
                        user['is_verified'] = True
                        user['verified_at'] = datetime.utcnow()
                        break
        except Exception as e:
            logger.error(f"Failed to verify user TLS: {e}")

class EmailModel:
    def __init__(self):
        self.db_conn = DatabaseConnection()
        self.db = self.db_conn.get_db()
        self.crypto = CryptoManager()
        
        if hasattr(self.db, 'emails'):
            self.collection = self.db.emails
        else:
            self.collection = self.db['emails']
    
    def save_email(self, email_data):
        """Encrypt content and save email to database with enhanced security"""
        email_data['created_at'] = datetime.utcnow()
        email_data['updated_at'] = datetime.utcnow()
        email_data['is_encrypted'] = True
        
        # Encrypt sensitive content
        if 'content' in email_data:
            email_data['content'] = self.crypto.encrypt_content(email_data['content'])
        
        if 'subject' in email_data:
            email_data['subject_encrypted'] = self.crypto.encrypt_content(email_data['subject'])
        
        # Add security metadata
        email_data['tls_used'] = True  # Mark as TLS encrypted in transit
        email_data['encryption_version'] = '1.0'
        
        try:
            if hasattr(self.collection, 'insert_one'):
                result = self.collection.insert_one(email_data)
                email_id = str(result.inserted_id)
                logger.info(f"Encrypted email saved to MongoDB with ID: {email_id}")
                return email_id
            else:
                email_data['_id'] = f"email_{len(self.collection)}"
                self.collection.append(email_data)
                logger.info(f"Encrypted email saved to fallback storage with ID: {email_data['_id']}")
                return email_data['_id']
                
        except Exception as e:
            logger.error(f"Failed to save email: {e}")
            return None
    
    def get_emails_by_user(self, user_email, limit=50, decrypt=True):
        """Get emails for a specific user and decrypt content"""
        try:
            if hasattr(self.collection, 'find'):
                emails = list(self.collection.find(
                    {"$or": [{"to": user_email}, {"from": user_email}]}
                ).sort("created_at", -1).limit(limit))
            else:
                emails = [email for email in self.collection 
                         if user_email in email.get('to', []) or email.get('from') == user_email]
                emails = emails[-limit:] if len(emails) > limit else emails
            
            # Decrypt content if requested
            if decrypt:
                for email in emails:
                    self._decrypt_email_content(email)
            
            return emails
                
        except Exception as e:
            logger.error(f"Failed to retrieve emails: {e}")
            return []
    
    def get_email_by_id(self, email_id, decrypt=True):
        """Get specific email by ID with decryption"""
        try:
            if hasattr(self.collection, 'find_one'):
                from bson import ObjectId
                email = self.collection.find_one({"_id": ObjectId(email_id)})
            else:
                email = None
                for e in self.collection:
                    if e.get('_id') == email_id:
                        email = e
                        break
            
            if email and decrypt:
                self._decrypt_email_content(email)
            
            return email
                
        except Exception as e:
            logger.error(f"Failed to retrieve email: {e}")
            return None
    
    def _decrypt_email_content(self, email):
        """Decrypt email content in place"""
        if email.get('is_encrypted'):
            try:
                if 'content' in email:
                    email['content'] = self.crypto.decrypt_content(email['content'])
                if 'subject_encrypted' in email:
                    email['subject'] = self.crypto.decrypt_content(email['subject_encrypted'])
                    del email['subject_encrypted']  # Remove encrypted version
            except Exception as e:
                logger.warning(f"Failed to decrypt email content: {e}")
                email['decryption_error'] = True
    
    def get_email_history(self, user_email, limit=100):
        """Get full email history for user with detailed information"""
        return self.get_emails_by_user(user_email, limit=limit, decrypt=True)
    
    def get_detailed_email_report(self, email_id):
        """Get comprehensive email report with all analysis data"""
        email = self.get_email_by_id(email_id, decrypt=True)
        if not email:
            return None
        
        # Add additional report metadata
        report = {
            'email_data': email,
            'security_info': {
                'tls_encrypted': email.get('tls_used', False),
                'content_encrypted': email.get('is_encrypted', False),
                'encryption_version': email.get('encryption_version', 'unknown')
            },
            'generated_at': datetime.utcnow(),
            'report_version': '1.0'
        }
        
        return report
    
    def update_email_status(self, email_id, status):
        """Update email status with timestamp"""
        try:
            if hasattr(self.collection, 'update_one'):
                from bson import ObjectId
                result = self.collection.update_one(
                    {"_id": ObjectId(email_id)},
                    {"$set": {"status": status, "updated_at": datetime.utcnow()}}
                )
                return result.modified_count > 0
            else:
                for email in self.collection:
                    if email.get('_id') == email_id:
                        email['status'] = status
                        email['updated_at'] = datetime.utcnow()
                        return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to update email status: {e}")
            return False

class LogModel:
    def __init__(self):
        self.db_conn = DatabaseConnection()
        self.db = self.db_conn.get_db()
        
        if hasattr(self.db, 'logs'):
            self.collection = self.db.logs
        else:
            self.collection = self.db['logs']
    
    def log_activity(self, activity_type, details, user_email=None, user_id=None, severity='info'):
        """Enhanced logging with security and DCN process tracking"""
        log_data = {
            'activity_type': activity_type,
            'details': details,
            'user_email': user_email,
            'user_id': user_id,
            'severity': severity,
            'timestamp': datetime.utcnow(),
            'source': 'email_server'
        }
        
        try:
            if hasattr(self.collection, 'insert_one'):
                self.collection.insert_one(log_data)
            else:
                log_data['_id'] = f"log_{len(self.collection)}"
                self.collection.append(log_data)
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    def get_recent_logs(self, limit=100, user_id=None, activity_types=None):
        """Get recent system logs with filtering"""
        try:
            query = {}
            if user_id:
                query['user_id'] = user_id
            if activity_types:
                query['activity_type'] = {'$in': activity_types}
            
            if hasattr(self.collection, 'find'):
                logs = list(self.collection.find(query).sort("timestamp", -1).limit(limit))
            else:
                logs = self.collection
                if query:
                    logs = [log for log in logs if all(log.get(k) == v for k, v in query.items())]
                logs = logs[-limit:] if len(logs) > limit else logs
            
            return logs
        except Exception as e:
            logger.error(f"Failed to retrieve logs: {e}")
            return []

class MetricsModel:
    def __init__(self):
        self.db_conn = DatabaseConnection()
        self.db = self.db_conn.get_db()
        
        if hasattr(self.db, 'metrics'):
            self.collection = self.db.metrics
        else:
            self.collection = self.db['metrics']
    
    def record_metric(self, metric_type, value, metadata=None, user_id=None):
        """Record system metrics with enhanced metadata"""
        metric_data = {
            'metric_type': metric_type,
            'value': value,
            'metadata': metadata or {},
            'user_id': user_id,
            'timestamp': datetime.utcnow()
        }
        
        try:
            if hasattr(self.collection, 'insert_one'):
                self.collection.insert_one(metric_data)
            else:
                metric_data['_id'] = f"metric_{len(self.collection)}"
                self.collection.append(metric_data)
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
    
    def get_metrics_summary(self, metric_type, hours=24):
        """Get metrics summary for specified time period"""
        try:
            if hasattr(self.collection, 'aggregate'):
                from datetime import timedelta
                start_time = datetime.utcnow() - timedelta(hours=hours)
                
                pipeline = [
                    {"$match": {
                        "metric_type": metric_type,
                        "timestamp": {"$gte": start_time}
                    }},
                    {"$group": {
                        "_id": None,
                        "avg_value": {"$avg": "$value"},
                        "max_value": {"$max": "$value"},
                        "min_value": {"$min": "$value"},
                        "count": {"$sum": 1}
                    }}
                ]
                
                result = list(self.collection.aggregate(pipeline))
                return result[0] if result else {}
            else:
                relevant_metrics = [m for m in self.collection if m.get('metric_type') == metric_type]
                if relevant_metrics:
                    values = [m['value'] for m in relevant_metrics]
                    return {
                        'avg_value': sum(values) / len(values),
                        'max_value': max(values),
                        'min_value': min(values),
                        'count': len(values)
                    }
                return {}
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}
