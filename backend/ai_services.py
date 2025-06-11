import requests
import json
import logging
import re
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

def safe_parse_ai_response(content):
    """Safely parse AI response with fallback handling"""
    if not content:
        return {
            'is_spam': False,
            'confidence': 0.0,
            'reasons': ['Empty AI response'],
            'threat_level': 'low',
            'categories': []
        }
    
    try:
        # First try direct JSON parsing
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse AI response as JSON: {e}")
        
        # Try to extract JSON from the content if it's wrapped or malformed
        try:
            # Look for JSON-like pattern in the text
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except:
            pass
        
        # If all parsing fails, try to extract basic information
        try:
            is_spam = 'true' in content.lower() and 'is_spam' in content.lower()
            confidence_match = re.search(r'confidence[\'"]?\s*:\s*([0-9.]+)', content, re.IGNORECASE)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.0
            
            return {
                'is_spam': is_spam,
                'confidence': confidence,
                'reasons': ['Extracted from malformed AI response'],
                'threat_level': 'medium' if is_spam else 'low',
                'categories': ['spam'] if is_spam else []
            }
        except:
            # Final fallback
            return {
                'is_spam': False,
                'confidence': 0.0,
                'reasons': ['AI response parsing failed, defaulting to safe'],
                'threat_level': 'low',
                'categories': []
            }

class GroqClient:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = Config.GROQ_MODEL
    
    def make_request(self, messages, max_tokens=150, temperature=0.3):
        """Make request to Groq API with enhanced error handling"""
        if not self.api_key or self.api_key == 'your_groq_api_key_here':
            logger.warning("Groq API key not configured, using fallback analysis")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {e}")
            return None

class EnhancedSpamDetectionAgent:
    """Enhanced spam detection with comprehensive scam detection"""
    
    # Enhanced keyword categories for better detection
    FINANCIAL_SCAM_KEYWORDS = [
        'bank details', 'atm pin', 'cvv', 'credit card', 'debit card', 'banking password',
        'account number', 'routing number', 'sort code', 'iban', 'swift code',
        'pin number', 'security code', 'card details', 'financial information',
        'transfer money', 'wire transfer', 'bitcoin', 'cryptocurrency', 'crypto wallet',
        'paypal login', 'venmo', 'cash app', 'western union', 'money gram'
    ]
    
    SCHOLARSHIP_SCAM_KEYWORDS = [
        'scholarship', 'grant', 'award', 'prize', 'lottery', 'sweepstakes',
        'winner', 'congratulations', 'selected', 'chosen', 'lucky',
        'crore', 'lakh', 'million', 'billion', 'thousand dollars'
    ]
    
    URGENCY_KEYWORDS = [
        'urgent', 'immediate', 'expire', 'deadline', 'limited time', 'act now',
        'hurry', 'quick', 'fast', 'asap', 'emergency', 'critical',
        'final notice', 'last chance', 'expires today', 'time sensitive'
    ]
    
    AUTHORITY_IMPERSONATION = [
        'government', 'irs', 'tax office', 'police', 'fbi', 'customs',
        'immigration', 'court', 'legal action', 'warrant', 'arrest',
        'amazon', 'microsoft', 'google', 'apple', 'paypal', 'bank of',
        'wells fargo', 'chase', 'visa', 'mastercard'
    ]
    
    PHISHING_PATTERNS = [
        r'verify.*account.*immediately',
        r'suspended.*account',
        r'click.*here.*urgent',
        r'update.*payment.*info',
        r'confirm.*identity.*now',
        r'security.*alert.*action',
        r'unauthorized.*access.*detected',
        r'account.*will.*be.*closed',
        r'provide.*bank.*details',
        r'send.*atm.*pin',
        r'give.*cvv.*number',
        r'share.*password',
        r'transfer.*money.*urgent',
        r'claim.*prize.*now',
        r'scholarship.*worth.*crore'
    ]
    
    def __init__(self):
        self.groq_client = GroqClient()
    
    def analyze_email(self, email_content, subject="", sender=""):
        """Comprehensive spam analysis with enhanced scam detection"""
        print(f"[AI DEBUG] ===== ENHANCED SPAM ANALYSIS START =====")
        print(f"[AI DEBUG] Content: {email_content[:200]}...")
        print(f"[AI DEBUG] Subject: {subject}")
        print(f"[AI DEBUG] Sender: {sender}")
        
        # First run AI analysis with safe parsing
        ai_result = self._ai_spam_analysis(email_content, subject, sender)
        print(f"[AI DEBUG] AI Result: {ai_result}")
        
        # Then enhance with comprehensive rule-based analysis
        rule_result = self._comprehensive_rule_analysis(email_content, subject, sender)
        print(f"[AI DEBUG] Rule Result: {rule_result}")
        
        # Combine results intelligently
        combined_result = self._intelligent_combine_results(ai_result, rule_result)
        
        # Add keyword highlighting data
        combined_result['keywords_found'] = rule_result['keywords_found']
        combined_result['highlighted_patterns'] = rule_result['highlighted_patterns']
        
        print(f"[AI DEBUG] Final Combined Result: {combined_result}")
        print(f"[AI DEBUG] ===== ENHANCED SPAM ANALYSIS END =====")
        
        return combined_result
    
    def _ai_spam_analysis(self, email_content, subject, sender):
        """Enhanced AI-powered spam analysis"""
        messages = [
            {
                "role": "system",
                "content": """You are an expert fraud and spam detection system. Analyze emails for:
1. Financial scams (asking for bank details, ATM pins, CVV numbers)
2. Phishing attempts (fake organizations, urgent account actions)
3. Lottery/prize scams (fake winnings, scholarships)
4. Authority impersonation (fake government, companies)
5. Romance/relationship scams
6. Investment scams

Respond with valid JSON only: {
  "is_spam": true/false,
  "confidence": 0.0-1.0,
  "threat_level": "low/medium/high/critical",
  "categories": ["financial_scam", "phishing", "lottery_scam", "impersonation"],
  "reasons": ["specific reasons"]
}

Be especially alert to:
- Requests for financial information
- Fake prizes or scholarships
- Urgency tactics
- Poor grammar/spelling
- Suspicious sender domains"""
            },
            {
                "role": "user",
                "content": f"SENDER: {sender}\nSUBJECT: {subject}\n\nEMAIL CONTENT:\n{email_content[:800]}"
            }
        ]
        
        try:
            response = self.groq_client.make_request(messages, max_tokens=300, temperature=0.1)
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content'].strip()
                print(f"[AI DEBUG] Raw AI Response: {content}")
                # Use safe parsing
                result = safe_parse_ai_response(content)
                print(f"[AI DEBUG] Parsed AI Result: {result}")
                return result
            else:
                print(f"[AI DEBUG] No AI response received")
                return self._default_ai_result()
        except Exception as e:
            logger.error(f"AI spam analysis failed: {e}")
            print(f"[AI DEBUG] AI Analysis Exception: {e}")
            return self._default_ai_result()
    
    def _comprehensive_rule_analysis(self, content, subject, sender):
        """Enhanced comprehensive rule-based analysis"""
        text = (content + " " + subject + " " + sender).lower()
        
        print(f"[RULE DEBUG] Analyzing text: {text[:200]}...")
        
        # Find financial scam keywords
        financial_keywords = []
        for keyword in self.FINANCIAL_SCAM_KEYWORDS:
            if keyword.lower() in text:
                financial_keywords.append(keyword)
        
        # Find scholarship/prize scam keywords
        scholarship_keywords = []
        for keyword in self.SCHOLARSHIP_SCAM_KEYWORDS:
            if keyword.lower() in text:
                scholarship_keywords.append(keyword)
        
        # Find urgency keywords
        urgency_keywords = []
        for keyword in self.URGENCY_KEYWORDS:
            if keyword.lower() in text:
                urgency_keywords.append(keyword)
        
        # Find authority impersonation
        authority_keywords = []
        for keyword in self.AUTHORITY_IMPERSONATION:
            if keyword.lower() in text:
                authority_keywords.append(keyword)
        
        # Find pattern matches
        pattern_matches = []
        for pattern in self.PHISHING_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                pattern_matches.extend(matches)
        
        print(f"[RULE DEBUG] Financial keywords: {financial_keywords}")
        print(f"[RULE DEBUG] Scholarship keywords: {scholarship_keywords}")
        print(f"[RULE DEBUG] Urgency keywords: {urgency_keywords}")
        print(f"[RULE DEBUG] Authority keywords: {authority_keywords}")
        print(f"[RULE DEBUG] Pattern matches: {pattern_matches}")
        
        # Calculate enhanced scores with higher weights for dangerous content
        financial_score = len(financial_keywords) * 0.4  # High weight for financial requests
        scholarship_score = len(scholarship_keywords) * 0.3  # High weight for fake prizes
        urgency_score = len(urgency_keywords) * 0.2
        authority_score = len(authority_keywords) * 0.25
        pattern_score = len(pattern_matches) * 0.35
        
        # Additional suspicious indicators
        suspicious_indicators = self._check_enhanced_suspicious_indicators(content, subject, sender)
        indicator_score = len(suspicious_indicators) * 0.15
        
        # Special bonus for combinations that are almost always scams
        combination_bonus = 0.0
        if financial_keywords and (scholarship_keywords or urgency_keywords):
            combination_bonus = 0.5  # Financial info + prize/urgency = almost certain scam
            print(f"[RULE DEBUG] ⚠️ CRITICAL COMBINATION DETECTED: Financial + Prize/Urgency")
        
        if len(financial_keywords) >= 2:  # Multiple financial requests
            combination_bonus = max(combination_bonus, 0.4)
            print(f"[RULE DEBUG] ⚠️ MULTIPLE FINANCIAL REQUESTS DETECTED")
        
        total_score = min(
            financial_score + scholarship_score + urgency_score + 
            authority_score + pattern_score + indicator_score + combination_bonus, 
            1.0
        )
        
        print(f"[RULE DEBUG] Scores - Financial: {financial_score:.2f}, Scholarship: {scholarship_score:.2f}")
        print(f"[RULE DEBUG] Scores - Urgency: {urgency_score:.2f}, Authority: {authority_score:.2f}")
        print(f"[RULE DEBUG] Scores - Pattern: {pattern_score:.2f}, Indicator: {indicator_score:.2f}")
        print(f"[RULE DEBUG] Combination bonus: {combination_bonus:.2f}")
        print(f"[RULE DEBUG] Total score: {total_score:.2f}")
        
        # Determine threat level with lower thresholds for financial scams
        if total_score >= 0.7 or combination_bonus >= 0.4:
            threat_level = 'critical'
        elif total_score >= 0.4 or financial_keywords:
            threat_level = 'high'
        elif total_score >= 0.25:
            threat_level = 'medium'
        else:
            threat_level = 'low'
        
        # Lower threshold for spam detection - be more aggressive
        is_spam = total_score >= 0.25 or len(financial_keywords) > 0
        
        all_keywords = financial_keywords + scholarship_keywords + urgency_keywords + authority_keywords
        
        print(f"[RULE DEBUG] Final determination - Is Spam: {is_spam}, Threat: {threat_level}")
        
        return {
            'is_spam': is_spam,
            'confidence': total_score,
            'threat_level': threat_level,
            'keywords_found': all_keywords,
            'pattern_matches': pattern_matches,
            'highlighted_patterns': all_keywords + pattern_matches,
            'suspicious_indicators': suspicious_indicators,
            'reasons': self._generate_enhanced_reasons(
                financial_keywords, scholarship_keywords, urgency_keywords, 
                authority_keywords, pattern_matches, suspicious_indicators, combination_bonus
            ),
            'financial_keywords': financial_keywords,
            'scam_indicators': {
                'financial_requests': len(financial_keywords),
                'fake_prizes': len(scholarship_keywords),
                'urgency_tactics': len(urgency_keywords),
                'authority_impersonation': len(authority_keywords)
            }
        }
    
    def _check_enhanced_suspicious_indicators(self, content, subject, sender):
        """Check for additional suspicious indicators"""
        indicators = []
        
        # Excessive caps
        if len(re.findall(r'[A-Z]{3,}', content)) > 5:
            indicators.append("Excessive capital letters")
        
        # Multiple exclamations
        if len(re.findall(r'!{2,}', content)) > 3:
            indicators.append("Multiple exclamation marks")
        
        # Multiple dollar amounts or currency mentions
        currency_patterns = [r'\$\d+', r'\d+\s*crore', r'\d+\s*lakh', r'\d+\s*million', r'\d+\s*billion']
        currency_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in currency_patterns)
        if currency_count > 1:
            indicators.append(f"Multiple currency amounts mentioned ({currency_count})")
        
        # Suspicious URLs or domains
        if re.search(r'http[s]?://[^\s]+', content):
            indicators.append("Contains external links")
        
        # Misspelled common words/companies
        misspellings = ['amazzon', 'microsft', 'gooogle', 'payp4l', 'b4nk', 'governmnt']
        for misspelling in misspellings:
            if misspelling in content.lower():
                indicators.append(f"Contains misspelling: {misspelling}")
        
        # Poor grammar indicators
        grammar_issues = [
            r'\b(recieved|recieve)\b',  # received/receive
            r'\b(seperate|seperat)\b',  # separate
            r'\b(loosing|loose)\b',     # losing/lose
            r'\byou\s+just\s+received\b', # awkward phrasing
            r'\bgive\s+us\s+yr\b',      # text speak in formal context
        ]
        
        for pattern in grammar_issues:
            if re.search(pattern, content, re.IGNORECASE):
                indicators.append("Poor grammar/spelling detected")
                break
        
        # Suspicious sender domain
        if sender and '@' in sender:
            domain = sender.split('@')[1].lower()
            suspicious_domains = [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'  # Free email for business
            ]
            if any(susp in domain for susp in suspicious_domains) and ('scholarship' in content.lower() or 'award' in content.lower()):
                indicators.append("Suspicious sender domain for official communication")
        
        return indicators
    
    def _generate_enhanced_reasons(self, financial, scholarship, urgency, authority, patterns, indicators, combo_bonus):
        """Generate comprehensive reasons for spam detection"""
        reasons = []
        
        if financial:
            reasons.append(f"🚨 CRITICAL: Requests financial information ({', '.join(financial[:3])})")
        
        if scholarship:
            reasons.append(f"⚠️ Fake prize/scholarship indicators ({', '.join(scholarship[:3])})")
        
        if urgency:
            reasons.append(f"⏰ Creates false urgency ({', '.join(urgency[:2])})")
        
        if authority:
            reasons.append(f"👤 Possible authority impersonation ({', '.join(authority[:2])})")
        
        if patterns:
            reasons.append(f"🎣 Matches {len(patterns)} phishing patterns")
        
        if indicators:
            reasons.append(f"📊 Shows {len(indicators)} suspicious indicators")
        
        if combo_bonus >= 0.4:
            reasons.append("🔥 CRITICAL: High-risk scam pattern combination detected")
        
        return reasons if reasons else ["No specific spam indicators detected"]
    
    def _intelligent_combine_results(self, ai_result, rule_result):
        """Intelligently combine AI and rule-based results"""
        # Rule-based analysis is primary for financial scams (more reliable)
        base_result = rule_result.copy()
        
        if ai_result and ai_result.get('confidence', 0) > 0:
            # Take the higher confidence and more severe threat assessment
            ai_confidence = ai_result.get('confidence', 0)
            rule_confidence = rule_result.get('confidence', 0)
            
            # Use the higher confidence
            base_result['confidence'] = max(ai_confidence, rule_confidence)
            
            # If either system says it's spam, it's spam
            base_result['is_spam'] = ai_result.get('is_spam', False) or rule_result['is_spam']
            
            # Use the higher threat level
            threat_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            ai_threat = threat_levels.get(ai_result.get('threat_level', 'low'), 1)
            rule_threat = threat_levels.get(rule_result.get('threat_level', 'low'), 1)
            
            if ai_threat > rule_threat:
                base_result['threat_level'] = ai_result['threat_level']
            
            # Combine reasons
            ai_reasons = ai_result.get('reasons', [])
            rule_reasons = rule_result.get('reasons', [])
            all_reasons = list(set(ai_reasons + rule_reasons))  # Remove duplicates
            base_result['reasons'] = all_reasons
            
            # Combine categories
            ai_categories = ai_result.get('categories', [])
            rule_categories = base_result.get('categories', [])
            base_result['categories'] = list(set(ai_categories + rule_categories))
        
        return base_result
    
    def _default_ai_result(self):
        """Default AI result when API is unavailable"""
        return {
            'is_spam': False,
            'confidence': 0.0,
            'threat_level': 'low',
            'reasons': ['AI analysis unavailable - using enhanced rule-based detection'],
            'categories': []
        }

class CompositionAssistantAgent:
    def __init__(self):
        self.groq_client = GroqClient()
    
    def suggest_improvements(self, email_content, context=""):
        """Enhanced email composition suggestions with safe parsing"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert email writing assistant. Provide 3 specific, actionable suggestions to improve this email's clarity, tone, and professionalism. Respond in plain text, not JSON."
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nEmail to improve:\n{email_content[:800]}"
            }
        ]
        
        try:
            response = self.groq_client.make_request(messages, max_tokens=300)
            if response and 'choices' in response:
                suggestions = response['choices'][0]['message']['content'].strip()
                return suggestions if suggestions else "Consider reviewing grammar and clarity."
            return "AI writing assistant temporarily unavailable."
        except Exception as e:
            logger.error(f"Composition assistance failed: {e}")
            return "Consider reviewing your email for clarity, tone, and professionalism."
    
    def generate_subject_line(self, email_content):
        """Generate subject line options with fallback"""
        messages = [
            {
                "role": "system",
                "content": "Generate 3 subject line options for this email: Professional, Friendly, Urgent. Format as: Professional: [subject] | Friendly: [subject] | Urgent: [subject]"
            },
            {
                "role": "user",
                "content": email_content[:400]
            }
        ]
        
        try:
            response = self.groq_client.make_request(messages, max_tokens=100)
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content'].strip()
                
                # Parse the response
                subject_options = {}
                for line in content.split('|'):
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip().lower()
                            value = parts[1].strip()
                            subject_options[key] = value
                
                # Ensure we have all three options
                if not subject_options:
                    subject_options = {
                        'professional': 'Email Update',
                        'friendly': 'Quick Update',
                        'urgent': 'Important: Please Review'
                    }
                else:
                    # Fill missing options
                    if 'professional' not in subject_options:
                        subject_options['professional'] = 'Email Update'
                    if 'friendly' not in subject_options:
                        subject_options['friendly'] = 'Quick Update'
                    if 'urgent' not in subject_options:
                        subject_options['urgent'] = 'Important: Please Review'
                
                return subject_options
            return {
                'professional': 'Email Update',
                'friendly': 'Quick Update', 
                'urgent': 'Important: Please Review'
            }
        except Exception as e:
            logger.error(f"Subject generation failed: {e}")
            return {
                'professional': 'Email Update',
                'friendly': 'Quick Update',
                'urgent': 'Important: Please Review'
            }
    
    def analyze_tone(self, email_content):
        """Analyze email tone with fallback"""
        messages = [
            {
                "role": "system",
                "content": "Analyze the tone of this email. Respond with: Tone: [description] | Sentiment: [positive/negative/neutral] | Professionalism: [score 1-10]"
            },
            {
                "role": "user",
                "content": email_content[:500]
            }
        ]
        
        try:
            response = self.groq_client.make_request(messages, max_tokens=150)
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content'].strip()
                
                # Parse the response
                tone_analysis = {
                    'current_tone': 'neutral',
                    'sentiment': 'neutral',
                    'professionalism': 7
                }
                
                for part in content.split('|'):
                    if ':' in part:
                        key, value = part.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if 'tone' in key:
                            tone_analysis['current_tone'] = value
                        elif 'sentiment' in key:
                            tone_analysis['sentiment'] = value
                        elif 'professionalism' in key:
                            try:
                                tone_analysis['professionalism'] = int(re.search(r'\d+', value).group())
                            except:
                                tone_analysis['professionalism'] = 7
                
                return tone_analysis
            
            return {
                'current_tone': 'neutral',
                'sentiment': 'neutral',
                'professionalism': 7
            }
        except Exception as e:
            logger.error(f"Tone analysis failed: {e}")
            return {
                'current_tone': 'neutral',
                'sentiment': 'neutral', 
                'professionalism': 7
            }
    
    def generate_reply(self, original_email, context="", tone="professional"):
        """Generate reply suggestions with enhanced AI"""
        print(f"[COMPOSITION DEBUG] Generating reply for email: {original_email[:100]}...")
        
        messages = [
            {
                "role": "system",
                "content": f"Generate a {tone} email reply. Keep it concise, appropriate, and helpful. Consider the context if provided."
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nOriginal email to reply to:\n{original_email[:600]}"
            }
        ]
        
        try:
            response = self.groq_client.make_request(messages, max_tokens=250)
            if response and 'choices' in response:
                reply = response['choices'][0]['message']['content'].strip()
                print(f"[COMPOSITION DEBUG] Generated reply: {reply}")
                return reply
            
            print(f"[COMPOSITION DEBUG] No AI response, using fallback")
            return f"Thank you for your email. I will review your message and get back to you soon. (Generated with {tone} tone)"
        except Exception as e:
            logger.error(f"Reply generation failed: {e}")
            print(f"[COMPOSITION DEBUG] Reply generation error: {e}")
            return f"Thank you for your email. I will get back to you soon. (AI temporarily unavailable)"

class EmailCategorizationAgent:
    def __init__(self):
        self.groq_client = GroqClient()
    
    def categorize_email(self, email_content, subject="", sender=""):
        """Enhanced email categorization with fallback"""
        # Use rule-based categorization as primary
        rule_result = self._rule_based_categorization(email_content, subject, sender)
        
        # Try AI enhancement
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Categorize this email. Respond with: Category: [work/personal/promotional/notification/spam/other] | Priority: [high/medium/low] | Action: [yes/no]"
                },
                {
                    "role": "user",
                    "content": f"From: {sender}\nSubject: {subject}\n\nContent: {email_content[:300]}"
                }
            ]
            
            response = self.groq_client.make_request(messages, max_tokens=80)
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content'].strip()
                
                # Parse AI response and enhance rule result
                for part in content.split('|'):
                    if ':' in part:
                        key, value = part.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip().lower()
                        
                        if 'category' in key and value in ['work', 'personal', 'promotional', 'notification', 'spam', 'other']:
                            rule_result['category'] = value
                        elif 'priority' in key and value in ['high', 'medium', 'low']:
                            rule_result['priority'] = value
                        elif 'action' in key:
                            rule_result['action_required'] = value in ['yes', 'true']
        except Exception as e:
            logger.error(f"AI categorization failed: {e}")
        
        return rule_result
    
    def _rule_based_categorization(self, content, subject, sender):
        """Rule-based fallback categorization"""
        text = (content + " " + subject + " " + sender).lower()
        
        # Category detection
        if any(word in text for word in ['meeting', 'deadline', 'project', 'work', 'office', 'business']):
            category = 'work'
        elif any(word in text for word in ['unsubscribe', 'offer', 'sale', 'discount', 'buy', 'deal']):
            category = 'promotional'
        elif any(word in text for word in ['notification', 'alert', 'update', 'reminder', 'confirm']):
            category = 'notification'
        elif any(word in text for word in ['friend', 'family', 'personal', 'birthday', 'vacation']):
            category = 'personal'
        else:
            category = 'other'
        
        # Priority detection
        if any(word in text for word in ['urgent', 'asap', 'emergency', 'critical', 'immediate']):
            priority = 'high'
            urgency = 'urgent'
        elif any(word in text for word in ['important', 'please review', 'deadline', 'soon']):
            priority = 'medium'
            urgency = 'normal'
        else:
            priority = 'low'
            urgency = 'low'
        
        # Action required detection
        action_required = any(word in text for word in ['please', 'action', 'respond', 'reply', 'confirm', 'review'])
        
        return {
            'category': category,
            'priority': priority,
            'urgency': urgency,
            'action_required': action_required
        }

class EnhancedKeywordHighlighter:
    """Enhanced keyword highlighting with pattern matching"""
    
    def __init__(self):
        self.spam_detector = EnhancedSpamDetectionAgent()
    
    def highlight_keywords_in_content(self, content, keywords_found):
        """Highlight found keywords in content with enhanced styling"""
        if not content or not keywords_found:
            return content
        
        highlighted_content = content
        
        for keyword in keywords_found:
            # Case insensitive replacement with enhanced highlighting
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_content = pattern.sub(
                f'<span class="spam-keyword" title="Suspicious keyword detected" style="background-color: #ff6b6b; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; animation: pulse 2s infinite;">{keyword}</span>',
                highlighted_content
            )
        
        return highlighted_content
    
    def generate_keyword_report(self, email_content, subject="", sender=""):
        """Generate comprehensive keyword analysis report"""
        # Get spam analysis results
        spam_result = self.spam_detector.analyze_email(email_content, subject, sender)
        
        keywords_found = spam_result.get('keywords_found', [])
        pattern_matches = spam_result.get('pattern_matches', [])
        
        # Generate highlighted content
        highlighted_content = self.highlight_keywords_in_content(email_content, keywords_found)
        
        # Create comprehensive report
        report = {
            'keywords_detected': len(keywords_found),
            'pattern_matches': len(pattern_matches),
            'keywords_found': keywords_found,
            'pattern_matches': pattern_matches,
            'highlighted_content': highlighted_content,
            'risk_assessment': spam_result.get('threat_level', 'low'),
            'confidence_impact': spam_result.get('confidence', 0),
            'analysis_summary': f"Detected {len(keywords_found)} suspicious keywords and {len(pattern_matches)} phishing patterns",
            'recommendations': self._generate_recommendations(keywords_found, pattern_matches, spam_result),
            'scam_indicators': spam_result.get('scam_indicators', {}),
            'financial_keywords': spam_result.get('financial_keywords', [])
        }
        
        return report
    
    def _generate_recommendations(self, keywords, patterns, spam_result):
        """Generate recommendations based on comprehensive analysis"""
        recommendations = []
        
        financial_keywords = spam_result.get('financial_keywords', [])
        threat_level = spam_result.get('threat_level', 'low')
        
        if financial_keywords:
            recommendations.append("🚨 CRITICAL: Do not provide any financial information")
            recommendations.append("🚨 This appears to be a financial scam - report and delete")
            recommendations.append("🚨 Never share bank details, PINs, or CVV numbers via email")
        
        if threat_level in ['high', 'critical']:
            recommendations.append("⚠️ High threat level detected - exercise extreme caution")
            recommendations.append("⚠️ Verify sender identity through independent channels")
        
        if keywords:
            recommendations.append("Review email carefully for potential spam content")
            recommendations.append("Verify sender authenticity before taking any action")
        
        if patterns:
            recommendations.append("High phishing risk - do not click any links")
            recommendations.append("Do not provide personal or financial information")
        
        if len(keywords) > 5 or len(patterns) > 2 or financial_keywords:
            recommendations.append("Consider blocking sender and reporting as spam/scam")
        
        return recommendations if recommendations else ["Email appears to be safe"]
    
    def find_spam_keywords(self, content, subject=""):
        """Find spam keywords using the enhanced detector"""
        # This method is for backward compatibility
        spam_result = self.spam_detector.analyze_email(content, subject, "")
        return spam_result.get('keywords_found', [])
    
    def highlight_keywords(self, content, keywords):
        """Highlight keywords for backward compatibility"""
        return self.highlight_keywords_in_content(content, keywords)

# Main AI service integration
class EnhancedAIService:
    def __init__(self):
        self.spam_detector = EnhancedSpamDetectionAgent()
        self.composition_assistant = CompositionAssistantAgent()
        self.categorizer = EmailCategorizationAgent()
        self.keyword_highlighter = EnhancedKeywordHighlighter()
    
    def process_incoming_email(self, email_data):
        """Enhanced email processing with comprehensive analysis"""
        try:
            content = email_data.get('content', '')
            subject = email_data.get('subject', '')
            sender = email_data.get('from', '')
            
            print(f"[AI SERVICE DEBUG] Processing email from {sender}, subject: {subject}")
            
            # Enhanced spam detection with comprehensive analysis
            spam_analysis = self.spam_detector.analyze_email(content, subject, sender)
            
            # Email categorization (but mark as spam if detected)
            if spam_analysis.get('is_spam'):
                categorization = {
                    'category': 'spam',
                    'priority': 'high' if spam_analysis.get('threat_level') in ['high', 'critical'] else 'medium',
                    'urgency': 'urgent',
                    'action_required': False  # No action needed for spam
                }
            else:
                categorization = self.categorizer.categorize_email(content, subject, sender)
            
            # Keyword analysis and highlighting
            keyword_report = self.keyword_highlighter.generate_keyword_report(content, subject, sender)
            
            # Add comprehensive analysis to email data
            email_data['ai_analysis'] = {
                'spam_analysis': spam_analysis,
                'categorization': categorization,
                'keyword_analysis': keyword_report,
                'highlighted_content': keyword_report['highlighted_content'],
                'processed_at': datetime.utcnow().isoformat(),
                'analysis_version': '3.0',
                'parsing_successful': True
            }
            
            logger.info(f"Enhanced email processing completed - Keywords: {keyword_report['keywords_detected']}, Spam: {spam_analysis['is_spam']}, Threat: {spam_analysis['threat_level']}")
            return email_data
            
        except Exception as e:
            logger.error(f"Enhanced AI processing failed: {e}")
            # Provide minimal safe analysis
            email_data['ai_analysis'] = {
                'spam_analysis': {
                    'is_spam': False,
                    'confidence': 0.0,
                    'threat_level': 'low',
                    'reasons': ['Processing error - defaulting to safe']
                },
                'categorization': {
                    'category': 'other',
                    'priority': 'low',
                    'action_required': False
                },
                'keyword_analysis': {
                    'keywords_detected': 0,
                    'highlighted_content': email_data.get('content', ''),
                    'risk_assessment': 'unknown'
                },
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat(),
                'parsing_successful': False
            }
            return email_data
    
    def assist_composition(self, email_content, context="", tone="professional"):
        """Enhanced composition assistance with robust error handling"""
        try:
            # Get suggestions
            suggestions = self.composition_assistant.suggest_improvements(email_content, context)
            
            # Generate subject options
            subject_options = self.composition_assistant.generate_subject_line(email_content)
            
            # Analyze tone
            tone_analysis = self.composition_assistant.analyze_tone(email_content)
            
            return {
                'suggestions': suggestions,
                'subject_options': subject_options,
                'tone_analysis': tone_analysis,
                'generated_at': datetime.utcnow().isoformat(),
                'success': True
            }
        except Exception as e:
            logger.error(f"Composition assistance failed: {e}")
            return {
                'suggestions': 'AI writing assistant temporarily unavailable. Please review your email for clarity and professionalism.',
                'subject_options': {
                    'professional': 'Email Update',
                    'friendly': 'Quick Update',
                    'urgent': 'Important: Please Review'
                },
                'tone_analysis': {
                    'current_tone': 'neutral',
                    'sentiment': 'neutral',
                    'professionalism': 7
                },
                'error': str(e),
                'success': False
            }
    
    def generate_smart_reply(self, original_email, context="", tone="professional"):
        """Generate intelligent reply - MISSING FUNCTION ADDED"""
        try:
            print(f"[AI SERVICE DEBUG] ===== GENERATE SMART REPLY =====")
            print(f"[AI SERVICE DEBUG] Original email length: {len(original_email)}")
            print(f"[AI SERVICE DEBUG] Context: {context}")
            print(f"[AI SERVICE DEBUG] Tone: {tone}")
            
            # Use the composition assistant to generate reply
            reply = self.composition_assistant.generate_reply(original_email, context, tone)
            
            result = {
                'reply': reply,
                'tone': tone,
                'generated_at': datetime.utcnow().isoformat(),
                'success': True
            }
            
            print(f"[AI SERVICE DEBUG] Generated reply result: {result}")
            print(f"[AI SERVICE DEBUG] ===== END GENERATE SMART REPLY =====")
            
            return result
            
        except Exception as e:
            logger.error(f"Smart reply generation failed: {e}")
            print(f"[AI SERVICE DEBUG] Smart reply error: {e}")
            return {
                'reply': f"Thank you for your email. I will review your message and get back to you soon. (AI temporarily unavailable - {tone} tone)",
                'tone': tone,
                'generated_at': datetime.utcnow().isoformat(),
                'error': str(e),
                'success': False
            }

# Legacy compatibility
AIService = EnhancedAIService
