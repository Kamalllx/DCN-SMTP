
# AI Email System - Frontend Generation Guide

## 🎯 Project
Secure email system with SMTP/IMAP/POP3, TLS encryption, AI spam detection, and real-time protocol monitoring.

## 🔗 Core API Endpoints

### Auth
```
POST /api/auth/signup       # Create account
POST /api/auth/signin       # Login (returns JWT token)
```

### Email
```
GET /api/emails             # List user emails  
GET /api/email/{id}/report  # Detailed email analysis
POST /api/send-test-email   # Send new email
```

### AI Analysis  
```
POST /api/ai/comprehensive-analysis  # Full AI analysis
POST /api/ai/composition-help        # Writing assistance
POST /api/ai/generate-reply          # Smart reply
```

### System
```
GET /api/metrics           # System stats
POST /api/servers/start    # Start email servers
POST /api/servers/stop     # Stop email servers
```

### WebSocket Events
```
dcn_process      # Real-time protocol events
new_email        # New email notifications  
security_alert   # Threat alerts
```

## 🎨 Design Theme: Synthwave/Retrowave

**Colors:** Neon pink (#ff0080), electric blue (#00ffff), deep purple (#8a2be2), dark gradients
**Fonts:** Orbitron, Exo 2, Rajdhani (futuristic)
**Effects:** Neon glows, grid backgrounds, VHS scanlines, 80s retro vibes

## 📱 Required UI Components

1. **Auth Pages** - Signup/Login with TLS security indicators
2. **Email Inbox** - List with encryption badges, spam warnings, keywords highlighted  
3. **Email Composer** - Send with AI writing assistance
4. **Email Viewer** - Detailed reports with AI analysis breakdown
5. **DCN Monitor** - Real-time protocol visualization (SMTP/IMAP/POP3)
6. **Dashboard** - System metrics, threat counts, server status
7. **Server Controls** - Start/stop email servers

## 🔒 Key Features to Show

- TLS encryption status indicators
- AI spam/phishing detection results  
- Suspicious keyword highlighting (red overlay)
- Real-time protocol logs with color coding
- Email encryption badges
- Security threat levels (high/medium/low)

## 📊 Data Structure Examples

**Email Object:**
```
{
  "_id": "email_id",
  "from": "sender@example.com", 
  "subject": "Email subject",
  "content": "Decrypted content",
  "tls_used": true,
  "is_encrypted": true,
  "ai_analysis": {
    "spam_analysis": {
      "is_spam": false,
      "confidence": 0.85,
      "threat_level": "low"
    },
    "keyword_analysis": {
      "keywords_detected": 2,
      "keywords_found": ["urgent", "click"],
      "highlighted_content": "HTML with highlighted keywords"
    }
  }
}
```

**Authentication:**
All protected routes need: `Authorization: Bearer `

## 🚀 Tech Requirements

- Next.js/React with TypeScript
- WebSocket client for real-time updates  
- API integration with fetch/axios
- Responsive design with synthwave aesthetics
- Form validation and error handling

## 🎯 Priority Features

1. Secure authentication flow
2. Email management with AI analysis display
3. Real-time DCN protocol monitoring  
4. Synthwave UI with neon effects
5. Responsive design for all screen sizes