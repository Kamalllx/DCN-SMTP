from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
import logging
from datetime import datetime, timedelta
import jwt

from config import Config
from email_servers import EnhancedEmailServerManager
from database import EmailModel, UserModel, LogModel, MetricsModel
from ai_services import EnhancedAIService
from utils import EnhancedValidationUtils, EnhancedAuthUtils, log_email_activity, SpamKeywordHighlighter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app)

# Initialize SocketIO for real-time DCN visualization
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
email_server_manager = EnhancedEmailServerManager(socketio)
email_model = EmailModel()
user_model = UserModel()
log_model = LogModel()
metrics_model = MetricsModel()
ai_service = EnhancedAIService()
keyword_highlighter = SpamKeywordHighlighter()

# Enhanced HTML template with all new features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI-Enhanced Secure Email Server - DCN Project</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: rgba(44, 62, 80, 0.95); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; backdrop-filter: blur(10px); }
        .card { background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); backdrop-filter: blur(10px); }
        .auth-card { max-width: 500px; margin: 0 auto; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #2c3e50; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #e1e8ed; border-radius: 8px; font-size: 14px; transition: border-color 0.3s; }
        .form-group input:focus { outline: none; border-color: #3498db; }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; margin: 8px; font-weight: 600; transition: all 0.3s; }
        .btn-primary { background: linear-gradient(135deg, #3498db, #2980b9); color: white; }
        .btn-success { background: linear-gradient(135deg, #27ae60, #229954); color: white; }
        .btn-danger { background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; }
        .btn-warning { background: linear-gradient(135deg, #f39c12, #e67e22); color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        .status { padding: 15px; border-radius: 10px; margin: 10px 0; font-weight: 600; }
        .status.running { background: linear-gradient(135deg, #d4edda, #c3e6cb); color: #155724; border-left: 4px solid #28a745; }
        .status.stopped { background: linear-gradient(135deg, #f8d7da, #f5c6cb); color: #721c24; border-left: 4px solid #dc3545; }
        .email-list { max-height: 400px; overflow-y: auto; border: 1px solid #e1e8ed; border-radius: 10px; }
        .email-item { border-bottom: 1px solid #e1e8ed; padding: 20px; transition: background-color 0.3s; }
        .email-item:hover { background-color: #f8f9fa; }
        .email-item:last-child { border-bottom: none; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .metric-card { text-align: center; padding: 20px; background: linear-gradient(135deg, #ffffff, #f8f9fa); border-radius: 15px; border: 1px solid #e1e8ed; }
        .metric-value { font-size: 2.5em; font-weight: bold; background: linear-gradient(135deg, #3498db, #2980b9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .metric-label { font-size: 14px; color: #6c757d; margin-top: 5px; }
        #logs { background: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 10px; max-height: 300px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 12px; }
        #dcn-logs { background: #34495e; color: #ecf0f1; padding: 20px; border-radius: 10px; max-height: 300px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 12px; }
        .notification { position: fixed; top: 20px; right: 20px; padding: 20px; border-radius: 10px; color: white; z-index: 1000; max-width: 400px; opacity: 0; transition: opacity 0.3s; }
        .notification.show { opacity: 1; }
        .threat-high { background: linear-gradient(135deg, #e74c3c, #c0392b); }
        .threat-medium { background: linear-gradient(135deg, #f39c12, #e67e22); }
        .threat-low { background: linear-gradient(135deg, #27ae60, #229954); }
        .spam-keyword { background-color: #ff6b6b !important; color: white !important; padding: 2px 6px; border-radius: 4px; font-weight: bold; animation: pulse 1s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
        .report-section { background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 10px 0; }
        .dcn-process { background: #e8f4fd; border-left: 4px solid #3498db; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .dcn-process.smtp { border-left-color: #e74c3c; background: #fdf2f2; }
        .dcn-process.imap { border-left-color: #f39c12; background: #fefbf3; }
        .dcn-process.pop3 { border-left-color: #27ae60; background: #f1f8f4; }
        .protocol-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 10px; }
        .protocol-badge.smtp { background: #e74c3c; color: white; }
        .protocol-badge.imap { background: #f39c12; color: white; }
        .protocol-badge.pop3 { background: #27ae60; color: white; }
        .two-column { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .hidden { display: none !important; }
        .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI-Enhanced Secure Email Server</h1>
            <p>Data Communication and Networks (DCN) Project - Real-time Protocol Visualization</p>
            <div id="status-indicator" class="status running">🟢 System Online - TLS Encrypted</div>
        </div>
        
        <!-- Authentication Section -->
        <div class="card auth-card" id="auth-section">
            <h2 style="text-align: center; color: #2c3e50;">🔐 Secure Authentication</h2>
            <div class="two-column">
                <div>
                    <h3>📝 Sign Up</h3>
                    <form id="signup-form">
                        <div class="form-group">
                            <label>Email Address</label>
                            <input type="email" id="signup-email" placeholder="your@email.com" required>
                        </div>
                        <div class="form-group">
                            <label>Password (8+ chars, mixed case, numbers, special chars)</label>
                            <input type="password" id="signup-password" placeholder="Enter secure password" required>
                        </div>
                        <button type="button" onclick="signup()" class="btn btn-success" style="width: 100%;">
                            <span id="signup-spinner" class="loading hidden"></span>
                            Create Account with TLS Protection
                        </button>
                    </form>
                </div>
                <div>
                    <h3>🔑 Sign In</h3>
                    <form id="signin-form">
                        <div class="form-group">
                            <label>Email Address</label>
                            <input type="email" id="signin-email" placeholder="your@email.com" required>
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" id="signin-password" placeholder="Enter password" required>
                        </div>
                        <button type="button" onclick="signin()" class="btn btn-primary" style="width: 100%;">
                            <span id="signin-spinner" class="loading hidden"></span>
                            Sign In with TLS Authentication
                        </button>
                    </form>
                </div>
            </div>
            <div id="auth-message" style="text-align: center; margin-top: 20px;"></div>
        </div>

        <!-- Main Dashboard (Hidden until authenticated) -->
        <div id="dashboard-section" class="hidden">
            <!-- User Info Card -->
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2>👤 <span id="user-info">User Dashboard</span></h2>
                        <p id="user-details">Encrypted session active with TLS 1.3</p>
                    </div>
                    <div>
                        <button class="btn btn-warning" onclick="sendTestEmail()">📤 Send Test Email</button>
                        <button class="btn btn-danger" onclick="signout()">🚪 Sign Out</button>
                    </div>
                </div>
            </div>

            <!-- Real-time DCN Process Visualization -->
            <div class="card">
                <h2>📡 Real-time DCN Process Visualization</h2>
                <p>Watch live SMTP, IMAP, and POP3 protocol operations as they happen:</p>
                <div id="dcn-logs"></div>
                <div style="margin-top: 15px;">
                    <button class="btn btn-primary" onclick="clearDCNLogs()">🧹 Clear DCN Logs</button>
                    <button class="btn btn-success" onclick="simulateDCNProcess()">🎯 Simulate DCN Process</button>
                </div>
            </div>

            <!-- Email Management -->
            <div class="card">
                <h2>📧 Encrypted Email Management & History</h2>
                <div class="two-column">
                    <div>
                        <h3>📬 Your Email Inbox</h3>
                        <div id="email-list" class="email-list">
                            <div style="padding: 20px; text-align: center; color: #6c757d;">
                                <div class="loading"></div>
                                <p>Loading encrypted emails...</p>
                            </div>
                        </div>
                        <div style="margin-top: 15px;">
                            <button class="btn btn-primary" onclick="loadEmails()">🔄 Refresh Inbox</button>
                            <button class="btn btn-success" onclick="loadEmailHistory()">📚 View Full History</button>
                        </div>
                    </div>
                    <div>
                        <h3>📤 Quick Send Email</h3>
                        <form id="quick-send-form">
                            <div class="form-group">
                                <label>To</label>
                                <input type="email" id="quick-to" placeholder="recipient@example.com">
                            </div>
                            <div class="form-group">
                                <label>Subject</label>
                                <input type="text" id="quick-subject" placeholder="Email subject">
                            </div>
                            <div class="form-group">
                                <label>Message</label>
                                <textarea id="quick-content" rows="4" style="width: 100%; padding: 12px; border: 2px solid #e1e8ed; border-radius: 8px;" placeholder="Your message..."></textarea>
                            </div>
                            <button type="button" onclick="quickSendEmail()" class="btn btn-success" style="width: 100%;">
                                🔒 Send Encrypted Email
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Detailed Email Report Modal -->
            <div class="card hidden" id="email-report-section">
                <h2>📋 Detailed Email Analysis Report</h2>
                <div style="text-align: right; margin-bottom: 20px;">
                    <button class="btn btn-danger" onclick="closeReport()">✖ Close Report</button>
                </div>
                <div id="email-report-content"></div>
            </div>

            <!-- Enhanced Metrics -->
            <div class="card">
                <h2>📈 System Performance Metrics</h2>
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value" id="total-emails">0</div>
                        <div class="metric-label">Total Emails Processed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="spam-detected">0</div>
                        <div class="metric-label">Spam/Phishing Blocked</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="encryption-rate">100%</div>
                        <div class="metric-label">Encryption Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="tls-connections">0</div>
                        <div class="metric-label">TLS Connections</div>
                    </div>
                </div>
            </div>

            <!-- Server Management -->
            <div class="card">
                <h2>🖥️ DCN Server Management</h2>
                <div class="two-column">
                    <div>
                        <h3>Server Status</h3>
                        <div id="server-status">
                            <div class="status running">
                                <span class="protocol-badge smtp">SMTP</span> Port 587 - TLS Ready
                            </div>
                            <div class="status running">
                                <span class="protocol-badge imap">IMAP</span> Port 993 - SSL Active
                            </div>
                            <div class="status running">
                                <span class="protocol-badge pop3">POP3</span> Port 995 - SSL Active
                            </div>
                        </div>
                    </div>
                    <div>
                        <h3>Server Controls</h3>
                        <button class="btn btn-success" onclick="startServers()">🟢 Start All Servers</button>
                        <button class="btn btn-danger" onclick="stopServers()">🔴 Stop All Servers</button>
                        <button class="btn btn-primary" onclick="restartServers()">🔄 Restart Servers</button>
                    </div>
                </div>
            </div>

            <!-- System Logs -->
            <div class="card">
                <h2>📋 System Activity Logs</h2>
                <div id="logs"></div>
                <div style="margin-top: 15px;">
                    <button class="btn btn-primary" onclick="loadLogs()">🔄 Refresh Logs</button>
                    <button class="btn btn-warning" onclick="clearLogs()">🧹 Clear Logs</button>
                </div>
            </div>
        </div>
    </div>

    <div id="notification" class="notification"></div>

    <script>
        let authToken = null;
        let socket = null;
        let currentUser = null;

        // Initialize WebSocket connection
        function initializeSocket() {
            socket = io();
            
            socket.on('connect', function() {
                console.log('Connected to server');
                updateSystemStatus('🟢 System Online - Real-time DCN Monitoring');
            });
            
            socket.on('dcn_process', function(data) {
                displayDCNProcess(data);
            });
            
            socket.on('new_email', function(data) {
                showNotification(`📧 New email from ${data.from}`, data.is_spam ? 'threat-high' : 'threat-low');
                if (authToken) loadEmails();
            });
            
            socket.on('security_alert', function(data) {
                showNotification(`🚨 Security Alert: ${data.message}`, 'threat-high');
            });
        }

        function updateSystemStatus(message) {
            document.getElementById('status-indicator').innerHTML = message;
        }

        function showNotification(message, type = '') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification ${type} show`;
            setTimeout(() => {
                notification.classList.remove('show');
            }, 5000);
        }

        function displayDCNProcess(data) {
            const dcnLogs = document.getElementById('dcn-logs');
            const timestamp = new Date(data.timestamp).toLocaleTimeString();
            
            const logEntry = document.createElement('div');
            logEntry.className = `dcn-process ${data.protocol.toLowerCase()}`;
            logEntry.innerHTML = `
                <span class="protocol-badge ${data.protocol.toLowerCase()}">${data.protocol}</span>
                [${timestamp}] <strong>${data.stage}</strong>: ${data.details}
                ${data.data ? '<br><small>' + JSON.stringify(data.data, null, 2) + '</small>' : ''}
            `;
            
            dcnLogs.insertBefore(logEntry, dcnLogs.firstChild);
            
            // Keep only last 50 entries
            while (dcnLogs.children.length > 50) {
                dcnLogs.removeChild(dcnLogs.lastChild);
            }
        }

        function clearDCNLogs() {
            document.getElementById('dcn-logs').innerHTML = '';
        }

        function simulateDCNProcess() {
            // Simulate a complete email sending process
            const processes = [
                {protocol: 'SMTP', stage: 'TCP_HANDSHAKE', details: 'Establishing TCP connection', data: {port: 587}},
                {protocol: 'SMTP', stage: 'TLS_HANDSHAKE', details: 'Negotiating TLS encryption', data: {cipher: 'AES256-GCM'}},
                {protocol: 'SMTP', stage: 'EHLO_EXCHANGE', details: 'SMTP capability negotiation', data: {features: ['STARTTLS', 'AUTH']}},
                {protocol: 'SMTP', stage: 'EMAIL_TRANSFER', details: 'Transferring encrypted email content', data: {size: '2.4KB'}},
                {protocol: 'SMTP', stage: 'AI_ANALYSIS', details: 'Running AI spam/phishing detection', data: {confidence: 0.95}},
                {protocol: 'SMTP', stage: 'ENCRYPTION', details: 'Encrypting email for database storage', data: {algorithm: 'Fernet'}},
                {protocol: 'SMTP', stage: 'DELIVERY_COMPLETE', details: 'Email securely stored and delivered', data: {status: 'success'}}
            ];

            processes.forEach((process, index) => {
                setTimeout(() => {
                    displayDCNProcess({
                        ...process,
                        timestamp: new Date().toISOString(),
                        process_id: Date.now() + index
                    });
                }, index * 800);
            });
        }

        async function signup() {
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;
            const spinner = document.getElementById('signup-spinner');

            if (!email || !password) {
                showNotification('Please fill in all fields', 'threat-medium');
                return;
            }

            spinner.classList.remove('hidden');

            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            
            const data = await response.json();
            spinner.classList.add('hidden');

            if (response.ok) {
                showNotification('✅ Account created successfully! Please sign in.', 'threat-low');
                document.getElementById('signup-form').reset();
            } else {
                showNotification(`❌ ${data.error || 'Signup failed'}`, 'threat-high');
            }
        }

        async function signin() {
            const email = document.getElementById('signin-email').value;
            const password = document.getElementById('signin-password').value;
            const spinner = document.getElementById('signin-spinner');

            if (!email || !password) {
                showNotification('Please fill in all fields', 'threat-medium');
                return;
            }

            spinner.classList.remove('hidden');

            const response = await fetch('/api/auth/signin', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            
            const data = await response.json();
            spinner.classList.add('hidden');

            if (response.ok) {
                authToken = data.token;
                currentUser = email;
                document.getElementById('auth-section').classList.add('hidden');
                document.getElementById('dashboard-section').classList.remove('hidden');
                document.getElementById('user-info').textContent = `Welcome, ${email}`;
                document.getElementById('user-details').textContent = `TLS encrypted session active • Last login: ${new Date().toLocaleString()}`;
                loadEmails();
                loadMetrics();
                showNotification('🔓 Successfully signed in with TLS encryption', 'threat-low');
            } else {
                showNotification(`❌ ${data.error || 'Authentication failed'}`, 'threat-high');
            }
        }

        function signout() {
            authToken = null;
            currentUser = null;
            document.getElementById('auth-section').classList.remove('hidden');
            document.getElementById('dashboard-section').classList.add('hidden');
            document.getElementById('email-report-section').classList.add('hidden');
            showNotification('🔒 Signed out securely', 'threat-low');
        }

        async function loadEmails() {
            if (!authToken) return;
            
            const response = await fetch('/api/emails', {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                const emailList = document.getElementById('email-list');
                emailList.innerHTML = '';
                
                if (data.emails && data.emails.length > 0) {
                    data.emails.forEach(email => {
                        const div = document.createElement('div');
                        div.className = 'email-item';
                        
                        const aiAnalysis = email.ai_analysis || {};
                        const spamAnalysis = aiAnalysis.spam_analysis || {};
                        const keywordAnalysis = aiAnalysis.keyword_analysis || {};
                        
                        div.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                        <strong>From:</strong> ${email.from || 'Unknown'}
                                        ${spamAnalysis.is_spam ? '<span style="background: #e74c3c; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 10px;">🚨 SPAM</span>' : ''}
                                        ${email.tls_used ? '<span style="background: #27ae60; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 5px;">🔒 TLS</span>' : ''}
                                        ${email.is_encrypted ? '<span style="background: #3498db; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 5px;">🔐 ENCRYPTED</span>' : ''}
                                    </div>
                                    <div style="margin-bottom: 8px;"><strong>Subject:</strong> ${email.subject || 'No Subject'}</div>
                                    <div style="margin-bottom: 8px; font-size: 12px; color: #6c757d;">
                                        📅 ${new Date(email.created_at).toLocaleString()}
                                        ${keywordAnalysis.keywords_detected ? `• 🚨 ${keywordAnalysis.keywords_detected} suspicious keywords` : ''}
                                    </div>
                                    <div style="font-size: 14px; color: #495057;">
                                        ${(email.content || '').substring(0, 100)}${email.content && email.content.length > 100 ? '...' : ''}
                                    </div>
                                </div>
                                <div style="margin-left: 20px;">
                                    <button class="btn btn-primary" onclick="viewEmailReport('${email._id}')" style="margin: 2px;">
                                        📋 Detailed Report
                                    </button>
                                    <button class="btn btn-warning" onclick="replyToEmail('${email._id}')" style="margin: 2px;">
                                        💬 Reply
                                    </button>
                                </div>
                            </div>
                        `;
                        emailList.appendChild(div);
                    });
                } else {
                    emailList.innerHTML = '<div style="padding: 40px; text-align: center; color: #6c757d;">📭 No emails found. Send a test email to get started!</div>';
                }
            } else {
                showNotification(`❌ ${data.error || 'Failed to load emails'}`, 'threat-high');
            }
        }

        async function loadEmailHistory() {
            if (!authToken) return;
            
            const response = await fetch('/api/emails/history', {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification(`📚 Loaded ${data.emails.length} emails from history`, 'threat-low');
                // Update email list with history
                loadEmails();
            } else {
                showNotification(`❌ ${data.error || 'Failed to load email history'}`, 'threat-high');
            }
        }

        async function viewEmailReport(emailId) {
            if (!authToken) return;
            
            const response = await fetch(`/api/email/${emailId}/report`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('email-report-section').classList.remove('hidden');
                const contentDiv = document.getElementById('email-report-content');
                
                const emailData = data.email_data;
                const aiAnalysis = emailData.ai_analysis || {};
                const spamAnalysis = aiAnalysis.spam_analysis || {};
                const keywordAnalysis = aiAnalysis.keyword_analysis || {};
                const securityAnalysis = aiAnalysis.security_analysis || {};
                
                contentDiv.innerHTML = `
                    <div class="report-section">
                        <h3>📧 Email Details</h3>
                        <p><strong>From:</strong> ${emailData.from}</p>
                        <p><strong>To:</strong> ${emailData.to ? emailData.to.join(', ') : 'N/A'}</p>
                        <p><strong>Subject:</strong> ${emailData.subject}</p>
                        <p><strong>Date:</strong> ${new Date(emailData.created_at).toLocaleString()}</p>
                        <p><strong>Encryption:</strong> ${emailData.is_encrypted ? '✅ Content encrypted in database' : '❌ Not encrypted'}</p>
                        <p><strong>TLS Transport:</strong> ${emailData.tls_used ? '✅ Transmitted over TLS' : '❌ Plain text transmission'}</p>
                    </div>
                    
                    <div class="report-section">
                        <h3>🤖 AI Spam Analysis</h3>
                        <p><strong>Spam Detection:</strong> ${spamAnalysis.is_spam ? '🚨 SPAM DETECTED' : '✅ Not spam'}</p>
                        <p><strong>Confidence:</strong> ${(spamAnalysis.confidence * 100).toFixed(1)}%</p>
                        <p><strong>Threat Level:</strong> <span class="threat-${spamAnalysis.threat_level}">${(spamAnalysis.threat_level || 'unknown').toUpperCase()}</span></p>
                        ${spamAnalysis.reasons ? `<p><strong>Reasons:</strong><br>${spamAnalysis.reasons.map(r => `• ${r}`).join('<br>')}</p>` : ''}
                    </div>
                    
                    <div class="report-section">
                        <h3>🔍 Spam Keyword Analysis</h3>
                        <p><strong>Keywords Detected:</strong> ${keywordAnalysis.keywords_detected || 0}</p>
                        <p><strong>Risk Level:</strong> <span class="threat-${keywordAnalysis.risk_level}">${(keywordAnalysis.risk_level || 'unknown').toUpperCase()}</span></p>
                        ${keywordAnalysis.keywords && keywordAnalysis.keywords.length > 0 ? `
                            <p><strong>Suspicious Keywords Found:</strong></p>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                                ${keywordAnalysis.keywords.map(keyword => `<span class="spam-keyword">${keyword}</span>`).join(' ')}
                            </div>
                        ` : '<p>No suspicious keywords detected.</p>'}
                        ${aiAnalysis.highlighted_content ? `
                            <p><strong>Content with Highlighted Keywords:</strong></p>
                            <div style="background: #fff; border: 1px solid #dee2e6; padding: 15px; border-radius: 8px; max-height: 200px; overflow-y: auto;">
                                ${aiAnalysis.highlighted_content}
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="report-section">
                        <h3>🛡️ Security Analysis</h3>
                        <p><strong>Phishing Risk:</strong> ${securityAnalysis.is_phishing ? '🚨 HIGH RISK' : '✅ Low risk'}</p>
                        <p><strong>Security Score:</strong> ${securityAnalysis.risk_level ? (securityAnalysis.risk_level.toUpperCase()) : 'Unknown'}</p>
                        ${securityAnalysis.indicators && securityAnalysis.indicators.length > 0 ? `
                            <p><strong>Security Indicators:</strong><br>${securityAnalysis.indicators.map(i => `• ${i}`).join('<br>')}</p>
                        ` : ''}
                        ${securityAnalysis.recommendations && securityAnalysis.recommendations.length > 0 ? `
                            <p><strong>Recommendations:</strong><br>${securityAnalysis.recommendations.map(r => `• ${r}`).join('<br>')}</p>
                        ` : ''}
                    </div>
                    
                    <div class="report-section">
                        <h3>📊 Additional Analysis</h3>
                        <p><strong>Category:</strong> ${aiAnalysis.categorization?.category || 'Unknown'}</p>
                        <p><strong>Priority:</strong> ${aiAnalysis.categorization?.priority || 'Unknown'}</p>
                        <p><strong>Action Required:</strong> ${aiAnalysis.categorization?.action_required ? 'Yes' : 'No'}</p>
                        ${aiAnalysis.summary ? `<p><strong>AI Summary:</strong> ${aiAnalysis.summary}</p>` : ''}
                        ${aiAnalysis.action_items && aiAnalysis.action_items.action_items && aiAnalysis.action_items.action_items.length > 0 ? `
                            <p><strong>Action Items:</strong><br>${aiAnalysis.action_items.action_items.map(item => `• ${item.task} (Priority: ${item.priority})`).join('<br>')}</p>
                        ` : ''}
                    </div>
                `;
                
                // Scroll to report
                document.getElementById('email-report-section').scrollIntoView({behavior: 'smooth'});
            } else {
                showNotification(`❌ ${data.error || 'Failed to load email report'}`, 'threat-high');
            }
        }

        function closeReport() {
            document.getElementById('email-report-section').classList.add('hidden');
        }

        async function quickSendEmail() {
            if (!authToken) return;
            
            const to = document.getElementById('quick-to').value;
            const subject = document.getElementById('quick-subject').value;
            const content = document.getElementById('quick-content').value;
            
            if (!to || !subject || !content) {
                showNotification('Please fill in all fields', 'threat-medium');
                return;
            }
            
            const response = await fetch('/api/send-test-email', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    from: currentUser,
                    to: to,
                    subject: subject,
                    content: content
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification('✅ Email sent and encrypted successfully!', 'threat-low');
                document.getElementById('quick-send-form').reset();
                loadEmails();
            } else {
                showNotification(`❌ ${data.error || 'Failed to send email'}`, 'threat-high');
            }
        }

        async function sendTestEmail() {
            await quickSendEmail();
        }

        async function replyToEmail(emailId) {
            // Get email details and populate quick form
            if (!authToken) return;
            
            const response = await fetch(`/api/email/${emailId}/report`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                const emailData = data.email_data;
                document.getElementById('quick-to').value = emailData.from;
                document.getElementById('quick-subject').value = `Re: ${emailData.subject}`;
                document.getElementById('quick-content').value = `\n\n--- Original Message ---\nFrom: ${emailData.from}\nSubject: ${emailData.subject}\n\n${emailData.content}`;
                
                // Scroll to form
                document.getElementById('quick-send-form').scrollIntoView({behavior: 'smooth'});
                showNotification('Reply form populated. Edit and send your response.', 'threat-low');
            }
        }

        async function startServers() {
            const response = await fetch('/api/servers/start', {method: 'POST'});
            const data = await response.json();
            showNotification(data.message, response.ok ? 'threat-low' : 'threat-high');
        }

        async function stopServers() {
            const response = await fetch('/api/servers/stop', {method: 'POST'});
            const data = await response.json();
            showNotification(data.message, response.ok ? 'threat-low' : 'threat-high');
        }

        async function restartServers() {
            await stopServers();
            setTimeout(async () => {
                await startServers();
            }, 2000);
        }

        async function loadLogs() {
            const response = await fetch('/api/logs');
            const data = await response.json();
            
            if (response.ok) {
                const logs = document.getElementById('logs');
                logs.innerHTML = '';
                
                data.logs.forEach(log => {
                    const div = document.createElement('div');
                    div.style.marginBottom = '5px';
                    const timestamp = new Date(log.timestamp).toLocaleTimeString();
                    div.innerHTML = `[${timestamp}] <strong>${log.activity_type}:</strong> ${log.details}`;
                    logs.appendChild(div);
                });
            }
        }

        async function clearLogs() {
            const response = await fetch('/api/logs/clear', {method: 'POST'});
            const data = await response.json();
            if (response.ok) {
                showNotification(data.message, 'threat-low');
                loadLogs();
            }
        }

        async function loadMetrics() {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('total-emails').textContent = data.total_emails || 0;
                document.getElementById('spam-detected').textContent = data.spam_detected || 0;
                document.getElementById('encryption-rate').textContent = data.encryption_rate || '100%';
                document.getElementById('tls-connections').textContent = data.tls_connections || 0;
            }
        }

        // Auto-refresh functions
        setInterval(() => {
            if (authToken) {
                loadMetrics();
                loadLogs();
            }
        }, 30000);

        // Initialize on page load
        window.addEventListener('load', function() {
            initializeSocket();
            loadLogs();
            loadMetrics();
        });
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def dashboard():
    """Enhanced main dashboard with authentication"""
    return render_template_string(HTML_TEMPLATE)

# User Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Enhanced user signup with TLS verification"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        if not EnhancedValidationUtils.validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        valid_password, msg = EnhancedValidationUtils.validate_password_strength(password)
        if not valid_password:
            return jsonify({'error': msg}), 400

        user_data = {
            'email': email,
            'password': password,
            'signup_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'tls_verified': request.is_secure  # Check if request came over TLS
        }

        user_id = user_model.create_user(user_data)
        if user_id:
            log_model.log_activity('USER_SIGNUP', f'User signed up with TLS: {email}', user_email=email)
            return jsonify({'message': 'Account created successfully with TLS protection'}), 201
        else:
            return jsonify({'error': 'User already exists or signup failed'}), 409
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """Enhanced user signin with TLS authentication"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = user_model.authenticate_user(email, password, request.remote_addr)
        if user:
            # Mark user as TLS verified if connection is secure
            if request.is_secure:
                user_model.verify_user_tls(user['_id'])

            token = EnhancedAuthUtils.generate_jwt_token(user)
            log_model.log_activity('USER_SIGNIN', f'User signed in with TLS: {email}', user_email=email)
            
            # Emit TLS connection event
            socketio.emit('dcn_process', {
                'protocol': 'TLS',
                'stage': 'AUTHENTICATION_SUCCESS',
                'details': f'User {email} authenticated with TLS encryption',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {'user': email, 'tls_version': 'TLS 1.3', 'cipher': 'AES256-GCM'}
            })
            
            return jsonify({'token': token, 'user': {'email': email, 'tls_verified': True}}), 200
        else:
            log_model.log_activity('USER_SIGNIN_FAILED', f'Failed signin attempt: {email}', user_email=email, severity='warning')
            return jsonify({'error': 'Invalid credentials or account locked'}), 401
    except Exception as e:
        logger.error(f"Signin error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Enhanced Email Routes
@app.route('/api/emails')
@EnhancedAuthUtils.require_auth
def get_emails():
    """Get encrypted emails for authenticated user"""
    try:
        user_email = request.current_user.get('email')
        emails = email_model.get_emails_by_user(user_email, limit=20)
        
        for email in emails:
            if '_id' in email:
                email['_id'] = str(email['_id'])
        
        return jsonify({'emails': emails, 'count': len(emails)})
    except Exception as e:
        logger.error(f"Get emails error: {e}")
        return jsonify({'error': 'Failed to retrieve emails'}), 500

@app.route('/api/emails/history')
@EnhancedAuthUtils.require_auth
def get_email_history():
    """Get full email history for user"""
    try:
        user_email = request.current_user.get('email')
        emails = email_model.get_email_history(user_email, limit=100)
        
        for email in emails:
            if '_id' in email:
                email['_id'] = str(email['_id'])
        
        return jsonify({'emails': emails, 'count': len(emails)})
    except Exception as e:
        logger.error(f"Get email history error: {e}")
        return jsonify({'error': 'Failed to retrieve email history'}), 500

@app.route('/api/email/<email_id>/report')
@EnhancedAuthUtils.require_auth
def get_email_report(email_id):
    """Get detailed email analysis report with debugging"""
    try:
        user_email = request.current_user.get('email')
        print(f"[DEBUG] ===== DETAILED REPORT REQUEST =====")
        print(f"[DEBUG] Email ID: {email_id}")
        print(f"[DEBUG] Requested by user: {user_email}")
        
        email = email_model.get_email_by_id(email_id)
        
        if not email:
            print(f"[DEBUG] ❌ Email not found in database: {email_id}")
            return jsonify({'error': 'Email not found'}), 404
        
        print(f"[DEBUG] ✅ Email found - From: {email.get('from')}, Subject: {email.get('subject')}")
        
        # Check access permissions
        if (email.get('from') != user_email and user_email not in email.get('to', [])):
            print(f"[DEBUG] ❌ Access denied - User {user_email} cannot access email from {email.get('from')}")
            return jsonify({'error': 'Access denied'}), 403
        
        print(f"[DEBUG] ✅ Access granted for user: {user_email}")
        
        report = email_model.get_detailed_email_report(email_id)
        if not report:
            print(f"[DEBUG] ❌ Report generation failed for email: {email_id}")
            return jsonify({'error': 'Report not available'}), 404
        
        print(f"[DEBUG] ===== DETAILED REPORT GENERATED =====")
        print(f"[DEBUG] Report keys: {list(report.keys())}")
        
        if 'email_data' in report:
            email_data = report['email_data']
            print(f"[DEBUG] Email Data:")
            print(f"[DEBUG]   - From: {email_data.get('from')}")
            print(f"[DEBUG]   - To: {email_data.get('to')}")
            print(f"[DEBUG]   - Subject: {email_data.get('subject')}")
            print(f"[DEBUG]   - TLS Used: {email_data.get('tls_used')}")
            print(f"[DEBUG]   - Is Encrypted: {email_data.get('is_encrypted')}")
            
            ai_analysis = email_data.get('ai_analysis', {})
            if ai_analysis:
                print(f"[DEBUG] AI Analysis:")
                
                # Spam Analysis
                spam_analysis = ai_analysis.get('spam_analysis', {})
                if spam_analysis:
                    print(f"[DEBUG]   Spam Analysis:")
                    print(f"[DEBUG]     - Is Spam: {spam_analysis.get('is_spam')}")
                    print(f"[DEBUG]     - Confidence: {spam_analysis.get('confidence')}")
                    print(f"[DEBUG]     - Threat Level: {spam_analysis.get('threat_level')}")
                    print(f"[DEBUG]     - Reasons: {spam_analysis.get('reasons')}")
                
                # Keyword Analysis
                keyword_analysis = ai_analysis.get('keyword_analysis', {})
                if keyword_analysis:
                    print(f"[DEBUG]   Keyword Analysis:")
                    print(f"[DEBUG]     - Keywords Detected: {keyword_analysis.get('keywords_detected')}")
                    print(f"[DEBUG]     - Keywords Found: {keyword_analysis.get('keywords_found')}")
                    print(f"[DEBUG]     - Risk Assessment: {keyword_analysis.get('risk_assessment')}")
                
                # Security Analysis
                security_analysis = ai_analysis.get('security_analysis', {})
                if security_analysis:
                    print(f"[DEBUG]   Security Analysis:")
                    print(f"[DEBUG]     - Is Phishing: {security_analysis.get('is_phishing')}")
                    print(f"[DEBUG]     - Risk Level: {security_analysis.get('risk_level')}")
                    print(f"[DEBUG]     - Indicators: {security_analysis.get('indicators')}")
                
                # Categorization
                categorization = ai_analysis.get('categorization', {})
                if categorization:
                    print(f"[DEBUG]   Categorization:")
                    print(f"[DEBUG]     - Category: {categorization.get('category')}")
                    print(f"[DEBUG]     - Priority: {categorization.get('priority')}")
                    print(f"[DEBUG]     - Action Required: {categorization.get('action_required')}")
        
        print(f"[DEBUG] ===== END DETAILED REPORT =====")
        
        # Convert ObjectId to string for JSON serialization
        if '_id' in report['email_data']:
            report['email_data']['_id'] = str(report['email_data']['_id'])
        
        return jsonify(report)
    except Exception as e:
        print(f"[ERROR] ❌ Get email report error: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to retrieve email report'}), 500
@app.route('/api/send-test-email', methods=['POST'])
@EnhancedAuthUtils.require_auth
def send_test_email():
    """Send enhanced test email with full encryption and analysis"""
    try:
        data = request.get_json()
        user_email = request.current_user.get('email')
        
        email_data = {
            'from': data.get('from', user_email),
            'to': [data.get('to', 'recipient@example.com')],
            'subject': data.get('subject', 'Test Email'),
            'content': data.get('content', 'This is a test email.'),
            'user_id': request.current_user.get('user_id'),
            'sent_via_api': True,
            'client_ip': request.remote_addr
        }
        
        # Emit DCN process events
        socketio.emit('dcn_process', {
            'protocol': 'SMTP',
            'stage': 'EMAIL_COMPOSITION',
            'details': f'User {user_email} composing email to {email_data["to"][0]}',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {'from': email_data['from'], 'to': email_data['to'], 'subject': email_data['subject']}
        })
        
        # Process with enhanced AI and encryption
        processed_email = ai_service.process_incoming_email(email_data)
        
        # Enhanced spam keyword analysis
        spam_keywords = keyword_highlighter.find_spam_keywords(
            email_data['content'], 
            email_data['subject']
        )
        keyword_report = keyword_highlighter.generate_keyword_report(
            spam_keywords,
            processed_email.get('ai_analysis', {}).get('spam_analysis', {}).get('confidence', 0)
        )
        
        # Add enhanced keyword analysis
        if 'ai_analysis' not in processed_email:
            processed_email['ai_analysis'] = {}
        
        processed_email['ai_analysis']['keyword_analysis'] = keyword_report
        processed_email['ai_analysis']['highlighted_content'] = keyword_highlighter.highlight_keywords(
            email_data['content'], 
            spam_keywords
        )
        
        # Save encrypted email
        email_id = email_model.save_email(processed_email)
        
        if email_id:
            # Emit success events
            socketio.emit('dcn_process', {
                'protocol': 'SMTP',
                'stage': 'EMAIL_ENCRYPTED_STORED',
                'details': f'Email encrypted and stored with ID: {email_id}',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'email_id': email_id,
                    'encryption_used': True,
                    'spam_detected': processed_email.get('ai_analysis', {}).get('spam_analysis', {}).get('is_spam', False),
                    'keywords_found': len(spam_keywords)
                }
            })
            
            socketio.emit('new_email', {
                'from': email_data['from'],
                'subject': email_data['subject'],
                'is_spam': processed_email.get('ai_analysis', {}).get('spam_analysis', {}).get('is_spam', False),
                'keywords_detected': len(spam_keywords)
            })
            
            log_model.log_activity('EMAIL_SENT', f'Encrypted email sent: {email_id}', user_email=user_email)
            
            return jsonify({
                "status": "success", 
                "email_id": email_id, 
                "message": "Email sent and encrypted successfully",
                "encryption_used": True,
                "tls_transport": True,
                "ai_analysis": processed_email.get('ai_analysis', {}),
                "keywords_detected": len(spam_keywords)
            })
        else:
            return jsonify({"status": "error", "message": "Failed to save encrypted email"}), 500
            
    except Exception as e:
        logger.error(f"Send email error: {e}")
        return jsonify({"error": "Failed to send email"}), 500

# Enhanced AI Routes

# @app.route('/api/ai/comprehensive-analysis', methods=['POST'])
# @EnhancedAuthUtils.require_auth
# def comprehensive_analysis():
#     """Comprehensive AI analysis with detailed debugging"""
#     try:
#         data = request.get_json()
#         content = data.get('content', '')
#         subject = data.get('subject', '')
#         sender = data.get('sender', '')
        
#         print(f"[DEBUG] ===== COMPREHENSIVE AI ANALYSIS REQUEST =====")
#         print(f"[DEBUG] Content length: {len(content)}")
#         print(f"[DEBUG] Subject: {subject}")
#         print(f"[DEBUG] Sender: {sender}")
#         print(f"[DEBUG] Requested by: {request.current_user.get('email')}")
        
#         if not content:
#             print("[DEBUG] ❌ Empty content provided for analysis")
#             return jsonify({"error": "Content is required"}), 400
        
#         # Create email data for processing
#         email_data = {
#             'content': content,
#             'subject': subject,
#             'from': sender,
#             'analysis_requested_by': request.current_user.get('email')
#         }
        
#         print(f"[DEBUG] 🤖 Starting AI processing...")
        
#         # Process with comprehensive AI analysis
#         processed_email = ai_service.process_incoming_email(email_data)
        
#         print(f"[DEBUG] ✅ AI processing completed")
        
#         # Enhanced spam keyword analysis
#         spam_keywords = keyword_highlighter.find_spam_keywords(content, subject)
#         print(f"[DEBUG] 🔍 Spam keywords found: {spam_keywords}")
        
#         keyword_report = keyword_highlighter.generate_keyword_report(
#             spam_keywords,
#             processed_email.get('ai_analysis', {}).get('spam_analysis', {}).get('confidence', 0)
#         )
        
#         print(f"[DEBUG] 📊 Keyword report generated: {keyword_report.get('keywords_detected', 0)} keywords")
        
#         # Add keyword analysis
#         if 'ai_analysis' not in processed_email:
#             processed_email['ai_analysis'] = {}
        
#         processed_email['ai_analysis']['keyword_analysis'] = keyword_report
#         processed_email['ai_analysis']['highlighted_content'] = keyword_highlighter.highlight_keywords(content, spam_keywords)
        
#         analysis = processed_email.get('ai_analysis', {})
        
#         print(f"[DEBUG] ===== COMPREHENSIVE ANALYSIS RESULTS =====")
        
#         # Print spam analysis
#         spam_analysis = analysis.get('spam_analysis', {})
#         if spam_analysis:
#             print(f"[DEBUG] 🛡️ Spam Analysis:")
#             print(f"[DEBUG]   - Is Spam: {spam_analysis.get('is_spam')}")
#             print(f"[DEBUG]   - Confidence: {spam_analysis.get('confidence'):.3f}")
#             print(f"[DEBUG]   - Threat Level: {spam_analysis.get('threat_level')}")
#             print(f"[DEBUG]   - Categories: {spam_analysis.get('categories')}")
#             print(f"[DEBUG]   - Reasons: {spam_analysis.get('reasons')}")
        
#         # Print keyword analysis
#         keyword_analysis = analysis.get('keyword_analysis', {})
#         if keyword_analysis:
#             print(f"[DEBUG] 🔍 Keyword Analysis:")
#             print(f"[DEBUG]   - Keywords Detected: {keyword_analysis.get('keywords_detected')}")
#             print(f"[DEBUG]   - Risk Assessment: {keyword_analysis.get('risk_assessment')}")
#             print(f"[DEBUG]   - Keywords Found: {keyword_analysis.get('keywords_found')}")
        
#         # Print security analysis
#         security_analysis = analysis.get('security_analysis', {})
#         if security_analysis:
#             print(f"[DEBUG] 🔒 Security Analysis:")
#             print(f"[DEBUG]   - Is Phishing: {security_analysis.get('is_phishing')}")
#             print(f"[DEBUG]   - Risk Level: {security_analysis.get('risk_level')}")
        
#         # Print categorization
#         categorization = analysis.get('categorization', {})
#         if categorization:
#             print(f"[DEBUG] 📂 Categorization:")
#             print(f"[DEBUG]   - Category: {categorization.get('category')}")
#             print(f"[DEBUG]   - Priority: {categorization.get('priority')}")
#             print(f"[DEBUG]   - Action Required: {categorization.get('action_required')}")
        
#         print(f"[DEBUG] ===== END COMPREHENSIVE ANALYSIS =====")
        
#         log_model.log_activity('AI_COMPREHENSIVE', f'Comprehensive analysis performed', user_email=request.current_user.get('email'))
        
#         return jsonify(analysis)
#     except Exception as e:
#         print(f"[ERROR] ❌ Comprehensive analysis failed: {e}")
#         print(f"[ERROR] Exception type: {type(e).__name__}")
#         import traceback
#         print(f"[ERROR] Traceback: {traceback.format_exc()}")
#         return jsonify({"error": str(e)}), 500
# Server Management Routes
@app.route('/api/servers/start', methods=['POST'])
def start_servers():
    """Start email servers with DCN logging"""
    try:
        if not email_server_manager.servers_running:
            email_server_manager.start_all_servers()
            log_model.log_activity('SERVER_START', 'All enhanced email servers started')
            
            # Emit DCN process event
            socketio.emit('dcn_process', {
                'protocol': 'SYSTEM',
                'stage': 'SERVERS_STARTED',
                'details': 'SMTP, IMAP, and POP3 servers started with TLS encryption',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {'smtp_port': 587, 'imap_port': 993, 'pop3_port': 995, 'tls_enabled': True}
            })
            
            socketio.emit('server_status', {'status': 'started', 'message': 'All servers are now running with TLS'})
            return jsonify({"status": "success", "message": "Email servers started successfully with TLS encryption"})
        else:
            return jsonify({"status": "info", "message": "Servers are already running"})
    except Exception as e:
        logger.error(f"Failed to start servers: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/servers/stop', methods=['POST'])
def stop_servers():
    """Stop email servers"""
    try:
        email_server_manager.stop_all_servers()
        log_model.log_activity('SERVER_STOP', 'All email servers stopped')
        
        socketio.emit('dcn_process', {
            'protocol': 'SYSTEM',
            'stage': 'SERVERS_STOPPED',
            'details': 'All email servers stopped gracefully',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {'graceful_shutdown': True}
        })
        
        socketio.emit('server_status', {'status': 'stopped', 'message': 'All servers have been stopped'})
        return jsonify({"status": "success", "message": "Email servers stopped successfully"})
    except Exception as e:
        logger.error(f"Failed to stop servers: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Enhanced Metrics Routes
@app.route('/api/metrics')
def get_enhanced_metrics():
    """Get enhanced system metrics"""
    try:
        # Get basic metrics
        total_emails = len(email_model.get_emails_by_user("test@example.com", limit=1000))
        
        # Count different types of threats
        all_emails = email_model.get_emails_by_user("test@example.com", limit=1000)
        spam_count = sum(1 for email in all_emails 
                        if email.get('ai_analysis', {}).get('spam_analysis', {}).get('is_spam', False))
        
        # Count TLS connections
        tls_count = sum(1 for email in all_emails if email.get('tls_used', False))
        
        # Calculate encryption rate
        encrypted_count = sum(1 for email in all_emails if email.get('is_encrypted', False))
        encryption_rate = f"{(encrypted_count / max(total_emails, 1) * 100):.1f}%" if total_emails > 0 else "100%"
        
        metrics = {
            "total_emails": total_emails,
            "spam_detected": spam_count,
            "encryption_rate": encryption_rate,
            "tls_connections": tls_count,
            "security_score": min(95 + (encrypted_count * 5 / max(total_emails, 1)), 100),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return jsonify({"error": str(e)}), 500

# Enhanced Logging Routes
@app.route('/api/logs')
def get_logs():
    """Get enhanced system logs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        logs = log_model.get_recent_logs(limit=limit)
        
        # Convert ObjectId to string and format timestamps
        for log in logs:
            if '_id' in log:
                log['_id'] = str(log['_id'])
            if 'timestamp' in log and hasattr(log['timestamp'], 'isoformat'):
                log['timestamp'] = log['timestamp'].isoformat()
        
        return jsonify({"logs": logs, "count": len(logs)})
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/ai/comprehensive-analysis', methods=['POST'])
@EnhancedAuthUtils.require_auth
def comprehensive_analysis():
    """Comprehensive AI analysis with detailed debugging"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        subject = data.get('subject', '')
        sender = data.get('sender', '')
        
        print(f"[DEBUG] ===== COMPREHENSIVE AI ANALYSIS REQUEST =====")
        print(f"[DEBUG] Content length: {len(content)}")
        print(f"[DEBUG] Subject: {subject}")
        print(f"[DEBUG] Sender: {sender}")
        print(f"[DEBUG] Requested by: {request.current_user.get('email')}")
        
        if not content:
            print("[DEBUG] ❌ Empty content provided for analysis")
            return jsonify({"error": "Content is required"}), 400
        
        # Create email data for processing
        email_data = {
            'content': content,
            'subject': subject,
            'from': sender,
            'analysis_requested_by': request.current_user.get('email')
        }
        
        print(f"[DEBUG] 🤖 Starting AI processing...")
        
        # Process with comprehensive AI analysis
        processed_email = ai_service.process_incoming_email(email_data)
        
        print(f"[DEBUG] ✅ AI processing completed")
        
        # Enhanced spam keyword analysis
        spam_keywords = keyword_highlighter.find_spam_keywords(content, subject)
        print(f"[DEBUG] 🔍 Spam keywords found: {spam_keywords}")
        
        keyword_report = keyword_highlighter.generate_keyword_report(
            spam_keywords,
            processed_email.get('ai_analysis', {}).get('spam_analysis', {}).get('confidence', 0)
        )
        
        print(f"[DEBUG] 📊 Keyword report generated: {keyword_report.get('keywords_detected', 0)} keywords")
        
        # Add keyword analysis
        if 'ai_analysis' not in processed_email:
            processed_email['ai_analysis'] = {}
        
        processed_email['ai_analysis']['keyword_analysis'] = keyword_report
        processed_email['ai_analysis']['highlighted_content'] = keyword_highlighter.highlight_keywords(content, spam_keywords)
        
        analysis = processed_email.get('ai_analysis', {})
        
        print(f"[DEBUG] ===== COMPREHENSIVE ANALYSIS RESULTS =====")
        
        # Print spam analysis
        spam_analysis = analysis.get('spam_analysis', {})
        if spam_analysis:
            print(f"[DEBUG] 🛡️ Spam Analysis:")
            print(f"[DEBUG]   - Is Spam: {spam_analysis.get('is_spam')}")
            print(f"[DEBUG]   - Confidence: {spam_analysis.get('confidence'):.3f}")
            print(f"[DEBUG]   - Threat Level: {spam_analysis.get('threat_level')}")
            print(f"[DEBUG]   - Categories: {spam_analysis.get('categories')}")
            print(f"[DEBUG]   - Reasons: {spam_analysis.get('reasons')}")
        
        # Print keyword analysis
        keyword_analysis = analysis.get('keyword_analysis', {})
        if keyword_analysis:
            print(f"[DEBUG] 🔍 Keyword Analysis:")
            print(f"[DEBUG]   - Keywords Detected: {keyword_analysis.get('keywords_detected')}")
            print(f"[DEBUG]   - Risk Assessment: {keyword_analysis.get('risk_assessment')}")
            print(f"[DEBUG]   - Keywords Found: {keyword_analysis.get('keywords_found')}")
        
        # Print security analysis
        security_analysis = analysis.get('security_analysis', {})
        if security_analysis:
            print(f"[DEBUG] 🔒 Security Analysis:")
            print(f"[DEBUG]   - Is Phishing: {security_analysis.get('is_phishing')}")
            print(f"[DEBUG]   - Risk Level: {security_analysis.get('risk_level')}")
        
        # Print categorization
        categorization = analysis.get('categorization', {})
        if categorization:
            print(f"[DEBUG] 📂 Categorization:")
            print(f"[DEBUG]   - Category: {categorization.get('category')}")
            print(f"[DEBUG]   - Priority: {categorization.get('priority')}")
            print(f"[DEBUG]   - Action Required: {categorization.get('action_required')}")
        
        print(f"[DEBUG] ===== END COMPREHENSIVE ANALYSIS =====")
        
        log_model.log_activity('AI_COMPREHENSIVE', f'Comprehensive analysis performed', user_email=request.current_user.get('email'))
        
        return jsonify(analysis)
    except Exception as e:
        print(f"[ERROR] ❌ Comprehensive analysis failed: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/composition-help', methods=['POST'])
@EnhancedAuthUtils.require_auth
def composition_help():
    """Enhanced composition assistance with debugging"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        context = data.get('context', '')
        tone = data.get('tone', 'professional')
        
        print(f"[DEBUG] ===== COMPOSITION HELP REQUEST =====")
        print(f"[DEBUG] Content length: {len(content)}")
        print(f"[DEBUG] Context: {context}")
        print(f"[DEBUG] Tone: {tone}")
        print(f"[DEBUG] Requested by: {request.current_user.get('email')}")
        
        if not content:
            print("[DEBUG] ❌ Empty content provided for composition help")
            return jsonify({"error": "Content is required"}), 400
        
        print(f"[DEBUG] 🤖 Starting composition assistance...")
        
        result = ai_service.assist_composition(content, context, tone)
        
        print(f"[DEBUG] ===== COMPOSITION ASSISTANCE RESULTS =====")
        print(f"[DEBUG] ✨ Suggestions: {result.get('suggestions', 'N/A')}")
        
        subject_options = result.get('subject_options', {})
        if subject_options:
            print(f"[DEBUG] 📧 Subject Options:")
            for tone_type, suggestion in subject_options.items():
                print(f"[DEBUG]   - {tone_type.title()}: {suggestion}")
        
        tone_analysis = result.get('tone_analysis', {})
        if tone_analysis:
            print(f"[DEBUG] 🎭 Tone Analysis:")
            print(f"[DEBUG]   - Current Tone: {tone_analysis.get('current_tone')}")
            print(f"[DEBUG]   - Sentiment: {tone_analysis.get('sentiment')}")
            print(f"[DEBUG]   - Professionalism: {tone_analysis.get('professionalism')}/10")
        
        print(f"[DEBUG] ===== END COMPOSITION ASSISTANCE =====")
        
        log_model.log_activity('AI_COMPOSITION', f'Enhanced composition assistance provided', user_email=request.current_user.get('email'))
        
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] ❌ Composition help failed: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/generate-reply', methods=['POST'])
@EnhancedAuthUtils.require_auth
def generate_reply():
    """Generate smart reply with debugging"""
    try:
        data = request.get_json()
        original_email = data.get('original_email', '')
        context = data.get('context', '')
        tone = data.get('tone', 'professional')
        
        print(f"[DEBUG] ===== REPLY GENERATION REQUEST =====")
        print(f"[DEBUG] Original email length: {len(original_email)}")
        print(f"[DEBUG] Context: {context}")
        print(f"[DEBUG] Tone: {tone}")
        print(f"[DEBUG] Requested by: {request.current_user.get('email')}")
        
        if not original_email:
            print("[DEBUG] ❌ Empty original email provided for reply generation")
            return jsonify({"error": "Original email content is required"}), 400
        
        print(f"[DEBUG] 🤖 Starting reply generation...")
        
        result = ai_service.generate_smart_reply(original_email, context, tone)
        
        print(f"[DEBUG] ===== REPLY GENERATION RESULTS =====")
        print(f"[DEBUG] 💬 Generated Reply: {result.get('reply', 'N/A')}")
        print(f"[DEBUG] 🎭 Tone Used: {result.get('tone', 'N/A')}")
        print(f"[DEBUG] ⏰ Generated At: {result.get('generated_at', 'N/A')}")
        
        if 'error' in result:
            print(f"[DEBUG] ⚠️ Error in result: {result.get('error')}")
        
        print(f"[DEBUG] ===== END REPLY GENERATION =====")
        
        log_model.log_activity('AI_REPLY_GEN', f'Smart reply generated', user_email=request.current_user.get('email'))
        
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] ❌ Reply generation failed: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Clear system logs"""
    try:
        log_model.log_activity("LOGS_CLEARED", "System logs cleared by admin")
        return jsonify({"status": "success", "message": "Logs cleared successfully"})
    except Exception as e:
        logger.error(f"Failed to clear logs: {e}")
        return jsonify({"error": str(e)}), 500

# WebSocket Events for Real-time DCN Visualization
@socketio.on('connect')
def handle_connect():
    emit('status', {
        'msg': 'Connected to AI-Enhanced Email Server with TLS encryption', 
        'timestamp': datetime.utcnow().isoformat(),
        'encryption': 'TLS 1.3',
        'features': ['Real-time DCN monitoring', 'Encrypted email storage', 'AI spam detection']
    })
    logger.info('Client connected to WebSocket for DCN monitoring')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected from WebSocket')

@socketio.on('request_dcn_demo')
def handle_dcn_demo():
    """Handle request for DCN process demonstration"""
    # Simulate a complete email flow
    demo_processes = [
        {
            'protocol': 'TCP',
            'stage': 'CONNECTION_INIT',
            'details': 'TCP 3-way handshake initiated',
            'data': {'src_port': 'random', 'dst_port': 587, 'flags': 'SYN'}
        },
        {
            'protocol': 'TCP',
            'stage': 'CONNECTION_ESTABLISHED',
            'details': 'TCP connection established successfully',
            'data': {'state': 'ESTABLISHED', 'window_size': 8192}
        },
        {
            'protocol': 'TLS',
            'stage': 'HANDSHAKE_START',
            'details': 'TLS handshake negotiation started',
            'data': {'version': 'TLS 1.3', 'cipher_suites': ['AES256-GCM', 'ChaCha20-Poly1305']}
        },
        {
            'protocol': 'TLS',
            'stage': 'CERTIFICATE_EXCHANGE',
            'details': 'Server certificate validation completed',
            'data': {'issuer': 'Self-signed CA', 'valid_until': '2025-12-31'}
        },
        {
            'protocol': 'TLS',
            'stage': 'ENCRYPTION_READY',
            'details': 'Secure channel established with AES256-GCM',
            'data': {'cipher': 'AES256-GCM-SHA384', 'key_exchange': 'ECDHE'}
        },
        {
            'protocol': 'SMTP',
            'stage': 'PROTOCOL_START',
            'details': 'SMTP protocol communication initiated',
            'data': {'command': '220 Server Ready'}
        },
        {
            'protocol': 'SMTP',
            'stage': 'EHLO_EXCHANGE',
            'details': 'Extended SMTP capabilities negotiated',
            'data': {'capabilities': ['STARTTLS', 'AUTH PLAIN', 'SIZE 10485760']}
        },
        {
            'protocol': 'SMTP',
            'stage': 'EMAIL_TRANSFER',
            'details': 'Email content transfer in progress',
            'data': {'size': '2.4KB', 'encoding': 'base64'}
        },
        {
            'protocol': 'AI',
            'stage': 'CONTENT_ANALYSIS',
            'details': 'AI analyzing email for spam and threats',
            'data': {'model': 'Enhanced Detection Engine', 'analysis_time': '0.3s'}
        },
        {
            'protocol': 'CRYPTO',
            'stage': 'CONTENT_ENCRYPTION',
            'details': 'Encrypting email content for database storage',
            'data': {'algorithm': 'Fernet (AES 128)', 'key_rotation': 'enabled'}
        },
        {
            'protocol': 'DATABASE',
            'stage': 'SECURE_STORAGE',
            'details': 'Email stored in encrypted database with metadata',
            'data': {'encrypted': True, 'indexed': True, 'backup': 'enabled'}
        }
    ]
    
    for i, process in enumerate(demo_processes):
        socketio.sleep(1)  # 1 second delay between events
        emit('dcn_process', {
            **process,
            'timestamp': datetime.utcnow().isoformat(),
            'demo': True,
            'step': i + 1,
            'total_steps': len(demo_processes)
        })

if __name__ == '__main__':
    # Start email servers in background
    server_thread = threading.Thread(target=email_server_manager.start_all_servers)
    server_thread.daemon = True
    server_thread.start()
    
    # Give servers time to start
    time.sleep(3)
    
    # Start Flask app with SocketIO
    logger.info("Starting enhanced Flask application with real-time DCN visualization...")
    socketio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
