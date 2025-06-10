import requests
import json
import logging
import re
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

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
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {e}")
            return None

class EnhancedSpamDetectionAgent:
    """Enhanced spam detection with comprehensive keyword analysis"""
    
    SPAM_KEYWORDS = [
        'winner', 'congratulations', 'claim now', 'urgent', 'free money',
        'click here', 'limited time', 'act now', 'prize', 'lottery',
        'viagra', 'casino', 'debt', 'loan', 'credit', 'inheritance',
        'nigerian prince', 'transfer', 'million dollars', 'verify account',
        'suspended', 'click immediately', 'confirm identity', 'expire today',
        'final notice', 'last chance', 'guaranteed', 'risk free',
        'make money fast', 'work from home', 'cash bonus', 'instant access'
    ]
    
    PHISHING_PATTERNS = [
        r'verify.*account.*immediately',
        r'suspended.*account',
        r'click.*here.*urgent',
        r'update.*payment.*info',
        r'confirm.*identity.*now',
        r'security.*alert.*action',
        r'unauthorized.*access.*detected',
        r'account.*will.*be.*closed'
    ]
    
    def __init__(self):
        self.groq_client = GroqClient()
    
    def analyze_email(self, email_content, subject="", sender=""):
        """Comprehensive spam analysis with enhanced keyword detection"""
        # First run AI analysis
        ai_result = self._ai_spam_analysis(email_content, subject, sender)
        
        # Then enhance with rule-based analysis
        rule_result = self._enhanced_rule_based_analysis(email_content, subject, sender)
        
        # Combine results
        combined_result = self._combine_analysis_results(ai_result, rule_result)
        
        # Add keyword highlighting data
        combined_result['keywords_found'] = rule_result['keywords_found']
        combined_result['highlighted_patterns'] = rule_result['highlighted_patterns']
        
        return combined_result
    
    def _ai_spam_analysis(self, email_content, subject, sender):
        """AI-powered spam analysis using Groq"""
        messages = [
            {
                "role": "system",
                "content": "You are an advanced spam detection expert. Analyze the email comprehensively and respond with JSON format: {'is_spam': true/false, 'confidence': 0.0-1.0, 'reasons': ['reason1', 'reason2'], 'threat_level': 'low/medium/high', 'categories': ['spam', 'phishing', 'scam']}"
            },
            {
                "role": "user",
                "content": f"Sender: {sender}\nSubject: {subject}\n\nContent: {email_content}"
            }
        ]
        
        try:
            response = self.groq_client.make_request(messages, max_tokens=200)
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content']
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse AI response as JSON")
                    return self._default_ai_result()
            else:
                return self._default_ai_result()
        except Exception as e:
            logger.error(f"AI spam analysis failed: {e}")
            return self._default_ai_result()
    
    def _enhanced_rule_based_analysis(self, content, subject, sender):
        """Enhanced rule-based analysis with keyword detection"""
        text = (content + " " + subject + " " + sender).lower()
        
        # Find exact keyword matches
        keywords_found = []
        for keyword in self.SPAM_KEYWORDS:
            if keyword.lower() in text:
                keywords_found.append(keyword)
        
        # Find pattern matches
        pattern_matches = []
        for pattern in self.PHISHING_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                pattern_matches.extend(matches)
        
        # Calculate scores
        keyword_score = len(keywords_found) * 0.15
        pattern_score = len(pattern_matches) * 0.25
        
        # Additional suspicious indicators
        suspicious_indicators = self._check_suspicious_indicators(content, subject, sender)
        indicator_score = len(suspicious_indicators) * 0.1
        
        total_score = min(keyword_score + pattern_score + indicator_score, 1.0)
        
        # Determine threat level
        if total_score >= 0.7:
            threat_level = 'high'
        elif total_score >= 0.4:
            threat_level = 'medium'
        else:
            threat_level = 'low'
        
        return {
            'is_spam': total_score >= 0.4,
            'confidence': total_score,
            'threat_level': threat_level,
            'keywords_found': keywords_found,
            'pattern_matches': pattern_matches,
            'highlighted_patterns': keywords_found + pattern_matches,
            'suspicious_indicators': suspicious_indicators,
            'reasons': self._generate_reasons(keywords_found, pattern_matches, suspicious_indicators)
        }
    
    def _check_suspicious_indicators(self, content, subject, sender):
        """Check for additional suspicious indicators"""
        indicators = []
        
        # Excessive caps
        if len(re.findall(r'[A-Z]{3,}', content)) > 5:
            indicators.append("Excessive capital letters")
        
        # Multiple exclamations
        if len(re.findall(r'!{2,}', content)) > 3:
            indicators.append("Multiple exclamation marks")
        
        # Multiple dollar amounts
        if len(re.findall(r'\$\d+', content)) > 2:
            indicators.append("Multiple dollar amounts mentioned")
        
        # Suspicious URLs
        if re.search(r'http[s]?://[^\s]+', content):
            indicators.append("Contains external links")
        
        # Email forwarding patterns
        if re.search(r'forward.*this.*email', content, re.IGNORECASE):
            indicators.append("Email forwarding request")
        
        # Time pressure
        time_pressure_words = ['urgent', 'hurry', 'expire', 'deadline', 'limited time']
        if sum(1 for word in time_pressure_words if word in content.lower()) > 2:
            indicators.append("Creates time pressure")
        
        return indicators
    
    def _generate_reasons(self, keywords, patterns, indicators):
        """Generate human-readable reasons for spam detection"""
        reasons = []
        
        if keywords:
            reasons.append(f"Contains {len(keywords)} spam keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
        
        if patterns:
            reasons.append(f"Matches {len(patterns)} phishing patterns")
        
        if indicators:
            reasons.append(f"Shows {len(indicators)} suspicious indicators")
        
        return reasons if reasons else ["No specific spam indicators detected"]
    
    def _combine_analysis_results(self, ai_result, rule_result):
        """Combine AI and rule-based analysis results"""
        # Use AI result as base if available, otherwise use rule-based
        if ai_result and ai_result.get('confidence', 0) > 0:
            base_result = ai_result.copy()
            # Enhance with rule-based findings
            base_result['confidence'] = max(ai_result.get('confidence', 0), rule_result['confidence'])
            base_result['is_spam'] = ai_result.get('is_spam', False) or rule_result['is_spam']
            
            # Combine reasons
            ai_reasons = ai_result.get('reasons', [])
            rule_reasons = rule_result.get('reasons', [])
            base_result['reasons'] = ai_reasons + rule_reasons
            
            # Use highest threat level
            threat_levels = {'low': 1, 'medium': 2, 'high': 3}
            ai_threat = threat_levels.get(ai_result.get('threat_level', 'low'), 1)
            rule_threat = threat_levels.get(rule_result.get('threat_level', 'low'), 1)
            
            if rule_threat > ai_threat:
                base_result['threat_level'] = rule_result['threat_level']
            
            return base_result
        else:
            # Use rule-based result if AI is not available
            return {
                'is_spam': rule_result['is_spam'],
                'confidence': rule_result['confidence'],
                'threat_level': rule_result['threat_level'],
                'reasons': rule_result['reasons'],
                'categories': ['spam'] if rule_result['is_spam'] else []
            }
    
    def _default_ai_result(self):
        """Default AI result when API is unavailable"""
        return {
            'is_spam': False,
            'confidence': 0.0,
            'threat_level': 'low',
            'reasons': ['AI analysis unavailable'],
            'categories': []
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
            'confidence_impact': len(keywords_found) * 0.15 + len(pattern_matches) * 0.25,
            'analysis_summary': f"Detected {len(keywords_found)} suspicious keywords and {len(pattern_matches)} phishing patterns",
            'recommendations': self._generate_recommendations(keywords_found, pattern_matches)
        }
        
        return report
    
    def _generate_recommendations(self, keywords, patterns):
        """Generate recommendations based on keyword analysis"""
        recommendations = []
        
        if keywords:
            recommendations.append("Review email carefully for potential spam content")
            recommendations.append("Verify sender authenticity before taking any action")
        
        if patterns:
            recommendations.append("High phishing risk - do not click any links")
            recommendations.append("Do not provide personal or financial information")
        
        if len(keywords) > 5 or len(patterns) > 2:
            recommendations.append("Consider blocking sender or marking as spam")
        
        return recommendations if recommendations else ["Email appears to be safe"]

# Integration with main AI service
class EnhancedAIService:
    def __init__(self):
        self.spam_detector = EnhancedSpamDetectionAgent()
        self.keyword_highlighter = EnhancedKeywordHighlighter()
        # ... other components from original ai_services.py
    
    def process_incoming_email(self, email_data):
        """Enhanced email processing with keyword highlighting"""
        try:
            content = email_data.get('content', '')
            subject = email_data.get('subject', '')
            sender = email_data.get('from', '')
            
            # Enhanced spam detection
            spam_analysis = self.spam_detector.analyze_email(content, subject, sender)
            
            # Keyword analysis and highlighting
            keyword_report = self.keyword_highlighter.generate_keyword_report(content, subject, sender)
            
            # Add comprehensive analysis to email data
            email_data['ai_analysis'] = {
                'spam_analysis': spam_analysis,
                'keyword_analysis': keyword_report,
                'highlighted_content': keyword_report['highlighted_content'],
                'processed_at': datetime.utcnow().isoformat(),
                'analysis_version': '2.0'
            }
            
            logger.info(f"Enhanced email processing completed - Keywords: {keyword_report['keywords_detected']}, Spam: {spam_analysis['is_spam']}")
            return email_data
            
        except Exception as e:
            logger.error(f"Enhanced AI processing failed: {e}")
            email_data['ai_analysis'] = {
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat()
            }
            return email_data

# Legacy compatibility
AIService = EnhancedAIService
