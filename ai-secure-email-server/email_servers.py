import smtplib
import imaplib
import poplib
import email
import socket
import threading
import ssl
import queue
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

from config import Config, SecurityConfig
from database import EmailModel, LogModel, MetricsModel, UserModel
from ai_services import EnhancedAIService
from utils import EnhancedValidationUtils, log_email_activity, TLSUtils, SpamKeywordHighlighter

logger = logging.getLogger(__name__)

class DCNProcessLogger:
    """Real-time DCN process logger for visualization"""
    
    def __init__(self, log_queue=None, socketio=None):
        self.log_queue = log_queue or queue.Queue()
        self.socketio = socketio
        self.process_id = 0
    
    def log_dcn_event(self, protocol, stage, details, data=None):
        """Log DCN process events for real-time visualization"""
        self.process_id += 1
        
        event = {
            'process_id': self.process_id,
            'protocol': protocol,
            'stage': stage,
            'details': details,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'dcn_process'
        }
        
        # Add to queue for processing
        self.log_queue.put(event)
        
        # Emit real-time via WebSocket if available
        if self.socketio:
            self.socketio.emit('dcn_process', event)
        
        # Also log to regular logging
        logger.info(f"DCN-{protocol}: {stage} - {details}")

class EnhancedSMTPServer:
    def __init__(self, log_queue=None, socketio=None):
        self.host = Config.HOST
        self.port = Config.SMTP_PORT
        self.ssl_context = TLSUtils.create_secure_context()
        self.email_model = EmailModel()
        self.user_model = UserModel()
        self.log_model = LogModel()
        self.ai_service = EnhancedAIService()
        self.running = False
        self.dcn_logger = DCNProcessLogger(log_queue, socketio)
        self.keyword_highlighter = SpamKeywordHighlighter()
        
        # Load SSL certificates
        try:
            self.ssl_context.load_cert_chain(Config.CERT_FILE, Config.KEY_FILE)
        except FileNotFoundError:
            logger.warning("SSL certificates not found, generating new ones...")
            TLSUtils.generate_self_signed_cert()
            self.ssl_context.load_cert_chain(Config.CERT_FILE, Config.KEY_FILE)
    
    def start_server(self):
        """Start SMTP server with enhanced DCN logging"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.dcn_logger.log_dcn_event(
                'SMTP', 'SERVER_START', 
                f'SMTP server listening on {self.host}:{self.port}',
                {'host': self.host, 'port': self.port, 'tls_enabled': True}
            )
            
            while self.running:
                try:
                    client_socket, client_address = server_socket.accept()
                    
                    self.dcn_logger.log_dcn_event(
                        'SMTP', 'TCP_ACCEPT', 
                        f'TCP connection accepted from {client_address}',
                        {'client_ip': client_address[0], 'client_port': client_address[1]}
                    )
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    self.dcn_logger.log_dcn_event(
                        'SMTP', 'ERROR', 
                        f'Server error: {e}',
                        {'error_type': type(e).__name__}
                    )
                    
        except Exception as e:
            self.dcn_logger.log_dcn_event(
                'SMTP', 'FATAL_ERROR', 
                f'Failed to start server: {e}',
                {'error_type': type(e).__name__}
            )
        finally:
            server_socket.close()
            self.dcn_logger.log_dcn_event('SMTP', 'SERVER_STOP', 'SMTP server stopped')
    
    def handle_client(self, client_socket, client_address):
        """Handle SMTP client with detailed DCN process logging"""
        try:
            # Step 1: Send SMTP greeting
            greeting = "220 localhost ESMTP AI-Enhanced Email Server Ready\r\n"
            client_socket.send(greeting.encode())
            
            self.dcn_logger.log_dcn_event(
                'SMTP', 'GREETING_SENT', 
                'SMTP 220 greeting sent to client',
                {'message': greeting.strip(), 'rfc': 'RFC 5321'}
            )
            
            email_data = {}
            data_mode = False
            email_content = ""
            tls_established = False
            authenticated_user = None
            
            while True:
                try:
                    data = client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                    
                    self.dcn_logger.log_dcn_event(
                        'SMTP', 'COMMAND_RECEIVED', 
                        f'Received command: {data}',
                        {'command': data, 'data_mode': data_mode}
                    )
                    
                    if data_mode:
                        if data == ".":
                            # End of email data
                            data_mode = False
                            email_data['content'] = email_content
                            email_data['received_at'] = datetime.utcnow()
                            email_data['tls_used'] = tls_established
                            email_data['authenticated_user'] = authenticated_user
                            
                            self.dcn_logger.log_dcn_event(
                                'SMTP', 'DATA_END', 
                                'Email data transmission completed',
                                {'size_bytes': len(email_content), 'tls_used': tls_established}
                            )
                            
                            # Process with AI and enhanced spam detection
                            processed_email = self._process_email_with_ai(email_data, client_address)
                            
                            # Save encrypted email to database
                            email_id = self.email_model.save_email(processed_email)
                            
                            if email_id:
                                response = "250 2.0.0 Message accepted for delivery\r\n"
                                client_socket.send(response.encode())
                                
                                self.dcn_logger.log_dcn_event(
                                    'SMTP', 'MESSAGE_ACCEPTED', 
                                    f'Email accepted and saved with ID: {email_id}',
                                    {
                                        'email_id': email_id, 
                                        'spam_detected': processed_email.get('ai_analysis', {}).get('spam_analysis', {}).get('is_spam', False),
                                        'encryption_used': True
                                    }
                                )
                            else:
                                response = "451 4.3.0 Requested action aborted: local error\r\n"
                                client_socket.send(response.encode())
                                
                                self.dcn_logger.log_dcn_event(
                                    'SMTP', 'MESSAGE_REJECTED', 
                                    'Email rejected due to storage error'
                                )
                            
                            email_content = ""
                        else:
                            email_content += data + "\n"
                    else:
                        response, special_action = self.process_smtp_command(data, email_data, client_socket, client_address)
                        client_socket.send(response.encode() + b"\r\n")
                        
                        # Handle special actions
                        if special_action == 'STARTTLS':
                            tls_established = self._handle_starttls(client_socket, client_address)
                        elif special_action == 'DATA':
                            data_mode = True
                        elif special_action == 'AUTH':
                            authenticated_user = self._handle_auth(client_socket, client_address)
                        elif special_action == 'QUIT':
                            break
                            
                except Exception as e:
                    self.dcn_logger.log_dcn_event(
                        'SMTP', 'CLIENT_ERROR', 
                        f'Error handling client: {e}',
                        {'error_type': type(e).__name__, 'client': str(client_address)}
                    )
                    break
                    
        except Exception as e:
            self.dcn_logger.log_dcn_event(
                'SMTP', 'CONNECTION_ERROR', 
                f'Connection error: {e}',
                {'error_type': type(e).__name__, 'client': str(client_address)}
            )
        finally:
            client_socket.close()
            self.dcn_logger.log_dcn_event(
                'SMTP', 'CONNECTION_CLOSED', 
                f'Connection closed for client {client_address}'
            )
    
    def process_smtp_command(self, command, email_data, client_socket, client_address):
        """Process SMTP commands with detailed logging"""
        command_upper = command.upper()
        
        if command_upper.startswith("EHLO") or command_upper.startswith("HELO"):
            domain = command.split(" ", 1)[1] if " " in command else "unknown"
            
            self.dcn_logger.log_dcn_event(
                'SMTP', 'EHLO_RECEIVED', 
                f'EHLO/HELO from domain: {domain}',
                {'domain': domain, 'rfc': 'RFC 5321 Section 4.1.1.1'}
            )
            
            response = "250-localhost Hello, pleased to meet you\r\n"
            response += "250-STARTTLS\r\n"
            response += "250-AUTH PLAIN LOGIN\r\n"
            response += "250 HELP"
            
            return response, None
        
        elif command_upper.startswith("MAIL FROM:"):
            sender = command.split(":", 1)[1].strip().strip("<>")
            
            self.dcn_logger.log_dcn_event(
                'SMTP', 'MAIL_FROM', 
                f'Sender specified: {sender}',
                {'sender': sender, 'rfc': 'RFC 5321 Section 4.1.1.2'}
            )
            
            if EnhancedValidationUtils.validate_email(sender):
                email_data['from'] = sender
                return "250 2.1.0 Sender OK", None
            return "550 5.1.7 Invalid sender address", None
        
        elif command_upper.startswith("RCPT TO:"):
            recipient = command.split(":", 1)[1].strip().strip("<>")
            
            self.dcn_logger.log_dcn_event(
                'SMTP', 'RCPT_TO', 
                f'Recipient specified: {recipient}',
                {'recipient': recipient, 'rfc': 'RFC 5321 Section 4.1.1.3'}
            )
            
            if EnhancedValidationUtils.validate_email(recipient):
                email_data.setdefault('to', []).append(recipient)
                return "250 2.1.5 Recipient OK", None
            return "550 5.1.1 Invalid recipient address", None
        
        elif command_upper.startswith("DATA"):
            self.dcn_logger.log_dcn_event(
                'SMTP', 'DATA_START', 
                'Data transmission initiated',
                {'rfc': 'RFC 5321 Section 4.1.1.4'}
            )
            
            return "354 Start mail input; end with <CRLF>.<CRLF>", 'DATA'
        
        elif command_upper.startswith("STARTTLS"):
            self.dcn_logger.log_dcn_event(
                'SMTP', 'STARTTLS_REQUEST', 
                'TLS upgrade requested',
                {'rfc': 'RFC 3207'}
            )
            
            return "220 2.0.0 Ready to start TLS", 'STARTTLS'
        
        elif command_upper.startswith("AUTH"):
            auth_method = command.split(" ", 2)[1] if len(command.split()) > 1 else "UNKNOWN"
            
            self.dcn_logger.log_dcn_event(
                'SMTP', 'AUTH_REQUEST', 
                f'Authentication requested: {auth_method}',
                {'method': auth_method, 'rfc': 'RFC 4954'}
            )
            
            return "235 2.7.0 Authentication successful", 'AUTH'
        
        elif command_upper.startswith("QUIT"):
            self.dcn_logger.log_dcn_event(
                'SMTP', 'QUIT_REQUEST', 
                'Client initiated connection termination',
                {'rfc': 'RFC 5321 Section 4.1.1.10'}
            )
            
            return "221 2.0.0 Goodbye", 'QUIT'
        
        else:
            self.dcn_logger.log_dcn_event(
                'SMTP', 'UNKNOWN_COMMAND', 
                f'Unknown command received: {command}',
                {'command': command}
            )
            
            return "500 5.5.1 Command not recognized", None
    
    def _handle_starttls(self, client_socket, client_address):
        """Handle STARTTLS upgrade with detailed logging"""
        try:
            self.dcn_logger.log_dcn_event(
                'SMTP', 'TLS_HANDSHAKE_START', 
                'Initiating TLS handshake',
                {'client': str(client_address)}
            )
            
            # Wrap socket with TLS
            tls_socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
            
            self.dcn_logger.log_dcn_event(
                'SMTP', 'TLS_HANDSHAKE_SUCCESS', 
                'TLS handshake completed successfully',
                {
                    'cipher': tls_socket.cipher(),
                    'version': tls_socket.version(),
                    'client': str(client_address)
                }
            )
            
            return True
            
        except Exception as e:
            self.dcn_logger.log_dcn_event(
                'SMTP', 'TLS_HANDSHAKE_FAILED', 
                f'TLS handshake failed: {e}',
                {'error': str(e), 'client': str(client_address)}
            )
            
            return False
    
    def _handle_auth(self, client_socket, client_address):
        """Handle SMTP authentication"""
        try:
            self.dcn_logger.log_dcn_event(
                'SMTP', 'AUTH_PROCESS', 
                'Processing authentication',
                {'client': str(client_address)}
            )
            
            # Simplified auth for demo - in real implementation, would handle PLAIN/LOGIN
            return "demo_user@example.com"
            
        except Exception as e:
            self.dcn_logger.log_dcn_event(
                'SMTP', 'AUTH_FAILED', 
                f'Authentication failed: {e}',
                {'error': str(e), 'client': str(client_address)}
            )
            
            return None
    
    def _process_email_with_ai(self, email_data, client_address):
        """Process email with enhanced AI analysis and spam keyword highlighting"""
        try:
            self.dcn_logger.log_dcn_event(
                'SMTP', 'AI_ANALYSIS_START', 
                'Starting AI analysis of email content'
            )
            
            # Enhanced AI processing
            processed_email = self.ai_service.process_incoming_email(email_data)
            
            # Enhanced spam keyword detection and highlighting
            content = email_data.get('content', '')
            subject = email_data.get('subject', '')
            
            spam_keywords = self.keyword_highlighter.find_spam_keywords(content, subject)
            keyword_report = self.keyword_highlighter.generate_keyword_report(
                spam_keywords, 
                processed_email.get('ai_analysis', {}).get('spam_analysis', {}).get('confidence', 0)
            )
            
            # Add keyword analysis to AI analysis
            if 'ai_analysis' not in processed_email:
                processed_email['ai_analysis'] = {}
            
            processed_email['ai_analysis']['keyword_analysis'] = keyword_report
            processed_email['ai_analysis']['highlighted_content'] = self.keyword_highlighter.highlight_keywords(content, spam_keywords)
            
            self.dcn_logger.log_dcn_event(
                'SMTP', 'AI_ANALYSIS_COMPLETE', 
                f'AI analysis completed - Spam: {processed_email.get("ai_analysis", {}).get("spam_analysis", {}).get("is_spam", False)}, Keywords: {len(spam_keywords)}',
                {
                    'spam_detected': processed_email.get('ai_analysis', {}).get('spam_analysis', {}).get('is_spam', False),
                    'keywords_found': len(spam_keywords),
                    'confidence': processed_email.get('ai_analysis', {}).get('spam_analysis', {}).get('confidence', 0)
                }
            )
            
            return processed_email
            
        except Exception as e:
            self.dcn_logger.log_dcn_event(
                'SMTP', 'AI_ANALYSIS_ERROR', 
                f'AI analysis failed: {e}',
                {'error': str(e)}
            )
            
            return email_data

class EnhancedIMAPServer:
    def __init__(self, log_queue=None, socketio=None):
        self.host = Config.HOST
        self.port = Config.IMAP_PORT
        self.ssl_context = TLSUtils.create_secure_context()
        self.email_model = EmailModel()
        self.user_model = UserModel()
        self.running = False
        self.dcn_logger = DCNProcessLogger(log_queue, socketio)
        
        try:
            self.ssl_context.load_cert_chain(Config.CERT_FILE, Config.KEY_FILE)
        except FileNotFoundError:
            TLSUtils.generate_self_signed_cert()
            self.ssl_context.load_cert_chain(Config.CERT_FILE, Config.KEY_FILE)
    
    def start_server(self):
        """Start IMAP server with DCN logging"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.dcn_logger.log_dcn_event(
                'IMAP', 'SERVER_START', 
                f'IMAP server listening on {self.host}:{self.port}',
                {'host': self.host, 'port': self.port, 'ssl_enabled': True}
            )
            
            while self.running:
                try:
                    client_socket, client_address = server_socket.accept()
                    
                    # Immediately wrap with SSL for IMAPS
                    try:
                        ssl_socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
                        
                        self.dcn_logger.log_dcn_event(
                            'IMAP', 'SSL_CONNECTION', 
                            f'SSL connection established from {client_address}',
                            {'client_ip': client_address[0], 'ssl_cipher': ssl_socket.cipher()}
                        )
                        
                        client_thread = threading.Thread(
                            target=self.handle_imap_client,
                            args=(ssl_socket, client_address)
                        )
                        client_thread.daemon = True
                        client_thread.start()
                        
                    except Exception as e:
                        self.dcn_logger.log_dcn_event(
                            'IMAP', 'SSL_HANDSHAKE_FAILED', 
                            f'SSL handshake failed: {e}',
                            {'client': str(client_address)}
                        )
                        client_socket.close()
                    
                except Exception as e:
                    self.dcn_logger.log_dcn_event(
                        'IMAP', 'CONNECTION_ERROR', 
                        f'Connection error: {e}'
                    )
                    
        except Exception as e:
            self.dcn_logger.log_dcn_event(
                'IMAP', 'SERVER_ERROR', 
                f'Server error: {e}'
            )
        finally:
            server_socket.close()
            self.dcn_logger.log_dcn_event('IMAP', 'SERVER_STOP', 'IMAP server stopped')
    
    def handle_imap_client(self, client_socket, client_address):
        """Handle IMAP client with detailed protocol logging"""
        try:
            # Send IMAP greeting
            greeting = "* OK IMAP4rev1 AI-Enhanced Email Server Ready\r\n"
            client_socket.send(greeting.encode())
            
            self.dcn_logger.log_dcn_event(
                'IMAP', 'GREETING_SENT', 
                'IMAP greeting sent',
                {'message': greeting.strip(), 'rfc': 'RFC 3501'}
            )
            
            authenticated_user = None
            selected_mailbox = None
            
            while True:
                try:
                    data = client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                    
                    self.dcn_logger.log_dcn_event(
                        'IMAP', 'COMMAND_RECEIVED', 
                        f'Received: {data}',
                        {'command': data}
                    )
                    
                    parts = data.split()
                    if len(parts) < 2:
                        response = "* BAD Invalid command\r\n"
                        client_socket.send(response.encode())
                        continue
                    
                    tag = parts[0]
                    command = parts[1].upper()
                    args = parts[2:] if len(parts) > 2 else []
                    
                    response = self.process_imap_command(tag, command, args, authenticated_user, selected_mailbox, client_address)
                    
                    # Update state based on successful commands
                    if command == "LOGIN" and response.startswith(f"{tag} OK"):
                        authenticated_user = args[0].strip('"') if args else None
                        self.dcn_logger.log_dcn_event(
                            'IMAP', 'USER_AUTHENTICATED', 
                            f'User authenticated: {authenticated_user}',
                            {'user': authenticated_user}
                        )
                    elif command == "SELECT" and response.startswith(f"{tag} OK"):
                        selected_mailbox = args[0].strip('"') if args else None
                        self.dcn_logger.log_dcn_event(
                            'IMAP', 'MAILBOX_SELECTED', 
                            f'Mailbox selected: {selected_mailbox}',
                            {'mailbox': selected_mailbox, 'user': authenticated_user}
                        )
                    elif command == "LOGOUT":
                        client_socket.send(response.encode() + b"\r\n")
                        break
                    
                    client_socket.send(response.encode() + b"\r\n")
                    
                except Exception as e:
                    self.dcn_logger.log_dcn_event(
                        'IMAP', 'COMMAND_ERROR', 
                        f'Error processing command: {e}',
                        {'error': str(e)}
                    )
                    break
                    
        except Exception as e:
            self.dcn_logger.log_dcn_event(
                'IMAP', 'CLIENT_ERROR', 
                f'Client handler error: {e}',
                {'error': str(e), 'client': str(client_address)}
            )
        finally:
            client_socket.close()
            self.dcn_logger.log_dcn_event(
                'IMAP', 'CONNECTION_CLOSED', 
                f'Connection closed for {client_address}'
            )
    
    def process_imap_command(self, tag, command, args, authenticated_user, selected_mailbox, client_address):
        """Process IMAP commands with detailed logging"""
        if command == "CAPABILITY":
            self.dcn_logger.log_dcn_event(
                'IMAP', 'CAPABILITY_REQUEST', 
                'Client requested capabilities',
                {'rfc': 'RFC 3501 Section 6.1.1'}
            )
            return f"* CAPABILITY IMAP4rev1 STARTTLS AUTH=PLAIN AUTH=LOGIN\r\n{tag} OK CAPABILITY completed"
        
        elif command == "LOGIN":
            if len(args) >= 2:
                username = args[0].strip('"')
                password = args[1].strip('"')
                
                self.dcn_logger.log_dcn_event(
                    'IMAP', 'LOGIN_ATTEMPT', 
                    f'Login attempt for user: {username}',
                    {'username': username, 'rfc': 'RFC 3501 Section 6.2.3'}
                )
                
                # Authenticate user
                user = self.user_model.authenticate_user(username, password, client_address[0])
                if user:
                    self.dcn_logger.log_dcn_event(
                        'IMAP', 'LOGIN_SUCCESS', 
                        f'Login successful for user: {username}'
                    )
                    return f"{tag} OK LOGIN completed"
                else:
                    self.dcn_logger.log_dcn_event(
                        'IMAP', 'LOGIN_FAILED', 
                        f'Login failed for user: {username}'
                    )
                    return f"{tag} NO LOGIN failed"
            return f"{tag} BAD LOGIN command incomplete"
        
        elif command == "LIST":
            self.dcn_logger.log_dcn_event(
                'IMAP', 'LIST_REQUEST', 
                'Client requested mailbox list',
                {'user': authenticated_user, 'rfc': 'RFC 3501 Section 6.3.8'}
            )
            return f'* LIST () "/" "INBOX"\r\n{tag} OK LIST completed'
        
        elif command == "SELECT":
            if args and authenticated_user:
                mailbox = args[0].strip('"')
                
                self.dcn_logger.log_dcn_event(
                    'IMAP', 'SELECT_REQUEST', 
                    f'Selecting mailbox: {mailbox}',
                    {'mailbox': mailbox, 'user': authenticated_user, 'rfc': 'RFC 3501 Section 6.3.1'}
                )
                
                emails = self.email_model.get_emails_by_user(authenticated_user)
                count = len(emails)
                
                return f"* {count} EXISTS\r\n* {count} RECENT\r\n* FLAGS (\\Seen \\Answered \\Flagged \\Deleted \\Draft)\r\n{tag} OK SELECT completed"
            return f"{tag} NO SELECT failed"
        
        elif command == "FETCH":
            if authenticated_user and selected_mailbox:
                self.dcn_logger.log_dcn_event(
                    'IMAP', 'FETCH_REQUEST', 
                    'Client requested message fetch',
                    {'user': authenticated_user, 'mailbox': selected_mailbox, 'rfc': 'RFC 3501 Section 6.4.5'}
                )
                return f"* 1 FETCH (FLAGS (\\Seen) RFC822.SIZE 1234 ENVELOPE (...))\r\n{tag} OK FETCH completed"
            return f"{tag} NO FETCH failed"
        
        elif command == "LOGOUT":
            self.dcn_logger.log_dcn_event(
                'IMAP', 'LOGOUT_REQUEST', 
                'Client initiated logout',
                {'user': authenticated_user, 'rfc': 'RFC 3501 Section 6.1.3'}
            )
            return f"* BYE IMAP4rev1 Server logging out\r\n{tag} OK LOGOUT completed"
        
        else:
            self.dcn_logger.log_dcn_event(
                'IMAP', 'UNKNOWN_COMMAND', 
                f'Unknown command: {command}',
                {'command': command}
            )
            return f"{tag} BAD Command not recognized"

class EnhancedPOP3Server:
    def __init__(self, log_queue=None, socketio=None):
        self.host = Config.HOST
        self.port = Config.POP3_PORT
        self.ssl_context = TLSUtils.create_secure_context()
        self.email_model = EmailModel()
        self.user_model = UserModel()
        self.running = False
        self.dcn_logger = DCNProcessLogger(log_queue, socketio)
        
        try:
            self.ssl_context.load_cert_chain(Config.CERT_FILE, Config.KEY_FILE)
        except FileNotFoundError:
            TLSUtils.generate_self_signed_cert()
            self.ssl_context.load_cert_chain(Config.CERT_FILE, Config.KEY_FILE)
    
    def start_server(self):
        """Start POP3 server with DCN logging"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.dcn_logger.log_dcn_event(
                'POP3', 'SERVER_START', 
                f'POP3 server listening on {self.host}:{self.port}',
                {'host': self.host, 'port': self.port, 'ssl_enabled': True}
            )
            
            while self.running:
                try:
                    client_socket, client_address = server_socket.accept()
                    
                    # Immediately wrap with SSL for POP3S
                    try:
                        ssl_socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
                        
                        self.dcn_logger.log_dcn_event(
                            'POP3', 'SSL_CONNECTION', 
                            f'SSL connection established from {client_address}',
                            {'client_ip': client_address[0]}
                        )
                        
                        client_thread = threading.Thread(
                            target=self.handle_pop3_client,
                            args=(ssl_socket, client_address)
                        )
                        client_thread.daemon = True
                        client_thread.start()
                        
                    except Exception as e:
                        self.dcn_logger.log_dcn_event(
                            'POP3', 'SSL_HANDSHAKE_FAILED', 
                            f'SSL handshake failed: {e}'
                        )
                        client_socket.close()
                    
                except Exception as e:
                    self.dcn_logger.log_dcn_event(
                        'POP3', 'CONNECTION_ERROR', 
                        f'Connection error: {e}'
                    )
                    
        except Exception as e:
            self.dcn_logger.log_dcn_event(
                'POP3', 'SERVER_ERROR', 
                f'Server error: {e}'
            )
        finally:
            server_socket.close()
            self.dcn_logger.log_dcn_event('POP3', 'SERVER_STOP', 'POP3 server stopped')
    
    def handle_pop3_client(self, client_socket, client_address):
        """Handle POP3 client with detailed protocol logging"""
        try:
            # Send POP3 greeting
            greeting = "+OK POP3 AI-Enhanced Email Server ready\r\n"
            client_socket.send(greeting.encode())
            
            self.dcn_logger.log_dcn_event(
                'POP3', 'GREETING_SENT', 
                'POP3 greeting sent',
                {'message': greeting.strip(), 'rfc': 'RFC 1939'}
            )
            
            authenticated_user = None
            
            while True:
                try:
                    data = client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                    
                    self.dcn_logger.log_dcn_event(
                        'POP3', 'COMMAND_RECEIVED', 
                        f'Received: {data}',
                        {'command': data}
                    )
                    
                    parts = data.split()
                    if not parts:
                        response = "-ERR Invalid command\r\n"
                        client_socket.send(response.encode())
                        continue
                    
                    command = parts[0].upper()
                    args = parts[1:] if len(parts) > 1 else []
                    
                    response = self.process_pop3_command(command, args, authenticated_user, client_address)
                    
                    # Update state based on successful commands
                    if command == "USER" and response.startswith("+OK"):
                        authenticated_user = args[0] if args else None
                    elif command == "QUIT":
                        client_socket.send(response.encode() + b"\r\n")
                        break
                    
                    client_socket.send(response.encode() + b"\r\n")
                    
                except Exception as e:
                    self.dcn_logger.log_dcn_event(
                        'POP3', 'COMMAND_ERROR', 
                        f'Error processing command: {e}'
                    )
                    break
                    
        except Exception as e:
            self.dcn_logger.log_dcn_event(
                'POP3', 'CLIENT_ERROR', 
                f'Client handler error: {e}',
                {'client': str(client_address)}
            )
        finally:
            client_socket.close()
            self.dcn_logger.log_dcn_event(
                'POP3', 'CONNECTION_CLOSED', 
                f'Connection closed for {client_address}'
            )
    
    def process_pop3_command(self, command, args, authenticated_user, client_address):
        """Process POP3 commands with detailed logging"""
        if command == "USER":
            if args and EnhancedValidationUtils.validate_email(args[0]):
                self.dcn_logger.log_dcn_event(
                    'POP3', 'USER_COMMAND', 
                    f'User specified: {args[0]}',
                    {'user': args[0], 'rfc': 'RFC 1939 Section 7'}
                )
                return f"+OK User {args[0]} accepted"
            return "-ERR Invalid user"
        
        elif command == "PASS":
            if authenticated_user:
                # Authenticate user
                user = self.user_model.authenticate_user(authenticated_user, args[0] if args else "", client_address[0])
                if user:
                    self.dcn_logger.log_dcn_event(
                        'POP3', 'AUTH_SUCCESS', 
                        f'Authentication successful for {authenticated_user}',
                        {'user': authenticated_user}
                    )
                    return "+OK Mailbox ready"
                else:
                    self.dcn_logger.log_dcn_event(
                        'POP3', 'AUTH_FAILED', 
                        f'Authentication failed for {authenticated_user}'
                    )
                    return "-ERR Authentication failed"
            return "-ERR No user specified"
        
        elif command == "STAT":
            if authenticated_user:
                self.dcn_logger.log_dcn_event(
                    'POP3', 'STAT_COMMAND', 
                    'Client requested mailbox status',
                    {'user': authenticated_user, 'rfc': 'RFC 1939 Section 5'}
                )
                
                emails = self.email_model.get_emails_by_user(authenticated_user, decrypt=False)
                total_size = sum(len(str(email.get('content', ''))) for email in emails)
                return f"+OK {len(emails)} {total_size}"
            return "-ERR Not authenticated"
        
        elif command == "LIST":
            if authenticated_user:
                self.dcn_logger.log_dcn_event(
                    'POP3', 'LIST_COMMAND', 
                    'Client requested message list',
                    {'user': authenticated_user, 'rfc': 'RFC 1939 Section 5'}
                )
                
                emails = self.email_model.get_emails_by_user(authenticated_user, decrypt=False)
                if args:  # LIST specific message
                    try:
                        msg_num = int(args[0])
                        if 1 <= msg_num <= len(emails):
                            size = len(str(emails[msg_num-1].get('content', '')))
                            return f"+OK {msg_num} {size}"
                        return "-ERR No such message"
                    except (ValueError, IndexError):
                        return "-ERR Invalid message number"
                else:  # LIST all messages
                    response = f"+OK {len(emails)} messages\r\n"
                    for i, email in enumerate(emails, 1):
                        size = len(str(email.get('content', '')))
                        response += f"{i} {size}\r\n"
                    response += "."
                    return response
            return "-ERR Not authenticated"
        
        elif command == "RETR":
            if authenticated_user and args:
                try:
                    msg_num = int(args[0])
                    emails = self.email_model.get_emails_by_user(authenticated_user)
                    if 1 <= msg_num <= len(emails):
                        self.dcn_logger.log_dcn_event(
                            'POP3', 'RETR_COMMAND', 
                            f'Retrieving message {msg_num}',
                            {'user': authenticated_user, 'message_num': msg_num, 'rfc': 'RFC 1939 Section 5'}
                        )
                        
                        email_content = str(emails[msg_num-1].get('content', ''))
                        return f"+OK {len(email_content)} octets\r\n{email_content}\r\n."
                    return "-ERR No such message"
                except (ValueError, IndexError):
                    return "-ERR Invalid message number"
            return "-ERR Not authenticated or invalid command"
        
        elif command == "DELE":
            if authenticated_user and args:
                self.dcn_logger.log_dcn_event(
                    'POP3', 'DELE_COMMAND', 
                    f'Marking message {args[0]} for deletion',
                    {'user': authenticated_user, 'message_num': args[0], 'rfc': 'RFC 1939 Section 5'}
                )
                return f"+OK Message {args[0]} deleted"
            return "-ERR Invalid command"
        
        elif command == "NOOP":
            self.dcn_logger.log_dcn_event(
                'POP3', 'NOOP_COMMAND', 
                'No operation command received',
                {'rfc': 'RFC 1939 Section 5'}
            )
            return "+OK"
        
        elif command == "QUIT":
            self.dcn_logger.log_dcn_event(
                'POP3', 'QUIT_COMMAND', 
                'Client initiated quit',
                {'user': authenticated_user, 'rfc': 'RFC 1939 Section 5'}
            )
            return "+OK POP3 server signing off"
        
        else:
            self.dcn_logger.log_dcn_event(
                'POP3', 'UNKNOWN_COMMAND', 
                f'Unknown command: {command}'
            )
            return "-ERR Command not recognized"

class EnhancedEmailServerManager:
    def __init__(self, socketio=None):
        self.log_queue = queue.Queue()
        self.socketio = socketio
        
        self.smtp_server = EnhancedSMTPServer(self.log_queue, socketio)
        self.imap_server = EnhancedIMAPServer(self.log_queue, socketio)
        self.pop3_server = EnhancedPOP3Server(self.log_queue, socketio)
        self.servers_running = False
        
        # Start log emitter thread
        if socketio:
            self.log_thread = threading.Thread(target=self._emit_logs)
            self.log_thread.daemon = True
            self.log_thread.start()
    
    def _emit_logs(self):
        """Emit logs to WebSocket clients for real-time visualization"""
        while True:
            try:
                event = self.log_queue.get(timeout=1)
                if self.socketio:
                    self.socketio.emit('dcn_process', event)
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error emitting logs: {e}")
    
    def start_all_servers(self):
        """Start all email servers"""
        if not self.servers_running:
            self.servers_running = True
            
            # Start servers in separate threads
            smtp_thread = threading.Thread(target=self.smtp_server.start_server)
            imap_thread = threading.Thread(target=self.imap_server.start_server)
            pop3_thread = threading.Thread(target=self.pop3_server.start_server)
            
            smtp_thread.daemon = True
            imap_thread.daemon = True
            pop3_thread.daemon = True
            
            smtp_thread.start()
            imap_thread.start()
            pop3_thread.start()
            
            logger.info("All enhanced email servers started successfully")
    
    def stop_all_servers(self):
        """Stop all email servers"""
        self.smtp_server.running = False
        self.imap_server.running = False
        self.pop3_server.running = False
        self.servers_running = False
        logger.info("All email servers stopped")

# Legacy compatibility
EmailServerManager = EnhancedEmailServerManager
SMTPServer = EnhancedSMTPServer
IMAPServer = EnhancedIMAPServer
POP3Server = EnhancedPOP3Server
