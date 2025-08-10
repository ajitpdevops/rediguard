"""LLM Service for threat analysis and conversational AI"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.core.redis_stack import redis_stack_client

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """LLM configuration model"""
    provider: str = "groq"
    api_key: Optional[str] = None
    model: str = "llama3-8b-8192"
    base_url: str = "https://api.groq.com/openai/v1"
    max_tokens: int = 1024
    temperature: float = 0.7


class LLMService:
    """LLM service for threat analysis and conversational AI"""
    
    def __init__(self):
        self.config = LLMConfig()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the LLM client"""
        try:
            # Try to get API key from environment or settings
            api_key = settings.groq_api_key or settings.llm_api_key
            
            if api_key:
                self.config.api_key = api_key
                self.client = httpx.AsyncClient(
                    base_url=self.config.base_url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                logger.info("LLM client initialized successfully")
            else:
                logger.warning("No LLM API key found - LLM features will be disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
    
    async def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self.client is not None and self.config.api_key is not None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get LLM service status"""
        available = await self.is_available()
        
        status = {
            "available": available,
            "provider": self.config.provider,
            "model": self.config.model,
            "features": []
        }
        
        if available:
            status["features"] = ["threat_explanation", "chat_interface"]
        
        return status
    
    async def explain_threat(self, alert_id: str) -> Dict[str, Any]:
        """Generate business-friendly explanation for a security alert"""
        if not await self.is_available():
            raise Exception("LLM service not available")
        
        try:
            # Get alert details from Redis
            alert_data = await self._get_alert_details(alert_id)
            
            if not alert_data:
                raise Exception(f"Alert {alert_id} not found")
            
            # Create prompt for threat explanation
            prompt = self._create_threat_explanation_prompt(alert_data)
            
            # Call LLM
            response = await self._call_llm(prompt)
            
            # Parse and structure response
            explanation = self._parse_threat_explanation(response)
            
            return {
                "alert_id": alert_id,
                "explanation": explanation,
                "generated_at": datetime.now().isoformat(),
                "model": self.config.model
            }
            
        except Exception as e:
            logger.error(f"Failed to explain threat {alert_id}: {e}")
            raise
    
    async def chat(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle conversational AI for security queries"""
        if not await self.is_available():
            raise Exception("LLM service not available")
        
        try:
            # Create prompt with context
            prompt = self._create_chat_prompt(message, context)
            
            # Call LLM
            response = await self._call_llm(prompt)
            
            # Analyze intent and extract suggestions
            intent = self._analyze_intent(message)
            suggestions = self._generate_suggestions(intent, context)
            
            return {
                "response": response,
                "intent": intent,
                "suggestions": suggestions,
                "timestamp": datetime.now().isoformat(),
                "model": self.config.model
            }
            
        except Exception as e:
            logger.error(f"Failed to process chat message: {e}")
            raise
    
    async def _call_llm(self, prompt: str) -> str:
        """Make API call to LLM provider"""
        if not self.client:
            raise Exception("LLM client not initialized")
        
        try:
            payload = {
                "model": self.config.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert assistant. Provide clear, concise, and actionable security insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise
    
    async def _get_alert_details(self, alert_id: str) -> Optional[Dict]:
        """Get alert details from Redis or return mock data"""
        try:
            client = redis_stack_client.client
            if client:
                # Try to get alert from Redis
                alert_key = f"alert:{alert_id}"
                alert_data = client.hgetall(alert_key)
                
                if alert_data:
                    # Convert bytes to strings
                    return {k.decode() if isinstance(k, bytes) else k: 
                           v.decode() if isinstance(v, bytes) else v 
                           for k, v in alert_data.items()}
            
            # Fallback to mock data that matches frontend alerts
            mock_alerts = {
                'alert_001': {
                    'alert_id': 'alert_001',
                    'title': 'Suspicious Login Pattern Detected',
                    'user_id': 'user_123',
                    'ip': '192.168.1.100',
                    'location': 'New York, US',
                    'event_type': 'anomalous_login',
                    'anomaly_score': '0.95',
                    'detection_method': 'ML Anomaly Detection',
                    'confidence': '95',
                    'related_events': '8',
                    'timestamp': datetime.now().isoformat(),
                    'description': 'User user_123 showing unusual login behavior from multiple locations within a short timeframe'
                },
                'alert_002': {
                    'alert_id': 'alert_002',
                    'title': 'Multiple Failed Login Attempts',
                    'user_id': 'unknown',
                    'ip': '203.0.113.45',
                    'location': 'Unknown',
                    'event_type': 'brute_force',
                    'anomaly_score': '0.85',
                    'detection_method': 'Rate Limiting',
                    'confidence': '90',
                    'related_events': '15',
                    'timestamp': datetime.now().isoformat(),
                    'description': 'Brute force attack detected with 15 failed login attempts in 5 minutes'
                },
                'alert_003': {
                    'alert_id': 'alert_003',
                    'title': 'Unusual Data Access Pattern',
                    'user_id': 'user_789',
                    'ip': '172.16.0.10',
                    'location': 'Tokyo, JP',
                    'event_type': 'data_exfiltration',
                    'anomaly_score': '0.88',
                    'detection_method': 'Behavior Analysis',
                    'confidence': '88',
                    'related_events': '12',
                    'timestamp': datetime.now().isoformat(),
                    'description': 'User accessing large volumes of sensitive data outside normal patterns'
                },
                'alert_004': {
                    'alert_id': 'alert_004',
                    'title': 'Off-Hours Administrative Access',
                    'user_id': 'admin_001',
                    'ip': '10.0.0.100',
                    'location': 'Berlin, DE',
                    'event_type': 'off_hours_access',
                    'anomaly_score': '0.65',
                    'detection_method': 'Time-based Rules',
                    'confidence': '75',
                    'related_events': '3',
                    'timestamp': datetime.now().isoformat(),
                    'description': 'Administrative access detected at 2:30 AM outside normal business hours'
                },
                'alert_005': {
                    'alert_id': 'alert_005',
                    'title': 'Unusual API Usage Spike',
                    'user_id': 'user_456',
                    'ip': '10.0.0.5',
                    'location': 'London, UK',
                    'event_type': 'api_abuse',
                    'anomaly_score': '0.55',
                    'detection_method': 'Threshold Monitoring',
                    'confidence': '70',
                    'related_events': '6',
                    'timestamp': datetime.now().isoformat(),
                    'description': 'API calls exceeded normal thresholds by 300% during automated testing'
                },
                'alert_006': {
                    'alert_id': 'alert_006',
                    'title': 'Privilege Escalation Attempt',
                    'user_id': 'user_567',
                    'ip': '192.168.1.50',
                    'location': 'San Francisco, US',
                    'event_type': 'privilege_escalation',
                    'anomaly_score': '0.92',
                    'detection_method': 'Permission Monitoring',
                    'confidence': '85',
                    'related_events': '4',
                    'timestamp': datetime.now().isoformat(),
                    'description': 'Unauthorized attempt to access admin functions and escalate privileges'
                }
            }
            
            return mock_alerts.get(alert_id)
            
        except Exception as e:
            logger.error(f"Failed to get alert details: {e}")
            return None
    
    def _create_threat_explanation_prompt(self, alert_data: Dict) -> str:
        """Create enhanced prompt for threat explanation"""
        
        # Create a more detailed alert context
        alert_context = f"""
SECURITY ALERT ANALYSIS REQUEST

Alert Information:
- Alert ID: {alert_data.get('alert_id', 'Unknown')}
- User: {alert_data.get('user_id', 'Unknown')}
- IP Address: {alert_data.get('ip', 'Unknown')}
- Location: {alert_data.get('location', 'Unknown')}
- Event Type: {alert_data.get('event_type', 'Unknown')}
- Anomaly Score: {alert_data.get('anomaly_score', 'Unknown')} (0.0 = normal, 1.0 = highly suspicious)
- Detection Method: {alert_data.get('detection_method', 'Unknown')}
- Timestamp: {alert_data.get('timestamp', 'Unknown')}
- Related Events: {alert_data.get('related_events', 'Unknown')}
- Confidence Level: {alert_data.get('confidence', 'Unknown')}%

TASK: Provide a comprehensive security threat analysis in the following EXACT JSON format:

{{
  "summary": "A clear, concise 2-3 sentence explanation of what this security event represents",
  "details": "Technical details about the detection, methods used, and specific indicators that triggered the alert",
  "risk_level": "high|medium|low - based on the anomaly score and threat type",
  "impact": "Specific business impact this threat could have - data breach, unauthorized access, system compromise, etc.",
  "recommendations": ["Action 1", "Action 2", "Action 3"]
}}

GUIDELINES:
- Use business-friendly language while maintaining technical accuracy
- Base risk_level on anomaly score: >0.8=high, 0.5-0.8=medium, <0.5=low
- Include specific user IDs, IPs, and technical details when relevant
- Recommendations should be an array of specific, immediate actions
- Consider the detection method and confidence when assessing urgency
- Respond with VALID JSON only - no markdown, no code blocks, no extra text"""

        return alert_context
    
    def _create_chat_prompt(self, message: str, context: Optional[Dict] = None) -> str:
        """Create prompt for chat interaction"""
        context_str = ""
        if context:
            context_str = f"Context: {json.dumps(context, indent=2)}\n\n"
        
        prompt = f"""
{context_str}User Question: {message}

As a cybersecurity expert, provide a helpful response about security monitoring, threat detection, or Redis-based security analytics. 
Be practical and actionable in your advice.
"""
        return prompt
    
    def _parse_threat_explanation(self, response: str) -> Dict[str, str]:
        """Parse LLM response into structured explanation"""
        try:
            # Try to parse as JSON first
            import re
            
            # Clean the response - remove any markdown formatting or extra text
            cleaned_response = response.strip()
            
            # Extract JSON if wrapped in markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(1)
            
            # Try to find the JSON object
            start_brace = cleaned_response.find('{')
            end_brace = cleaned_response.rfind('}')
            
            if start_brace != -1 and end_brace != -1:
                json_str = cleaned_response[start_brace:end_brace + 1]
                parsed = json.loads(json_str)
                
                # Handle nested JSON strings - if values are strings that look like JSON, parse them
                def parse_nested_json(value):
                    if isinstance(value, str) and value.strip().startswith('{'):
                        try:
                            return json.loads(value)
                        except json.JSONDecodeError:
                            return value
                    return value
                
                # Parse nested JSON if needed
                for key in parsed:
                    parsed[key] = parse_nested_json(parsed[key])
                
                # Validate required fields and provide defaults
                explanation = {
                    "summary": parsed.get("summary", "Security anomaly detected requiring investigation"),
                    "details": parsed.get("details", "Technical analysis unavailable"),
                    "risk_level": parsed.get("risk_level", "medium").lower(),
                    "impact": parsed.get("impact", "Potential security impact requires assessment"),
                    "recommendations": self._format_recommendations(parsed.get("recommendations", ["Review alert details and investigate further"]))
                }
                
                return explanation
                
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.warning(f"Failed to parse JSON response: {e}")
        
        # Fallback to simple text parsing
        lines = response.split('\n')
        
        # Try to extract structured information from text
        summary = ""
        details = ""
        risk_level = "medium"
        impact = ""
        recommendations = ""
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            line_lower = line.lower()
            if any(word in line_lower for word in ['summary', 'overview', 'what happened']):
                current_section = 'summary'
                continue
            elif any(word in line_lower for word in ['details', 'technical', 'analysis']):
                current_section = 'details'
                continue
            elif any(word in line_lower for word in ['risk', 'severity', 'threat level']):
                current_section = 'risk'
                # Extract risk level
                if any(word in line_lower for word in ['high', 'critical', 'severe']):
                    risk_level = 'high'
                elif any(word in line_lower for word in ['low', 'minor']):
                    risk_level = 'low'
                continue
            elif any(word in line_lower for word in ['impact', 'consequence', 'damage']):
                current_section = 'impact'
                continue
            elif any(word in line_lower for word in ['recommend', 'action', 'steps', 'next']):
                current_section = 'recommendations'
                continue
            
            # Add content to current section
            if current_section == 'summary':
                summary += line + " "
            elif current_section == 'details':
                details += line + " "
            elif current_section == 'impact':
                impact += line + " "
            elif current_section == 'recommendations':
                recommendations += line + "\n"
        
        # If no structured sections found, use the full response as summary
        if not summary and not details:
            summary = response[:300] + "..." if len(response) > 300 else response
            details = response
        
        return {
            "summary": summary.strip() or "Security alert detected requiring analysis",
            "details": details.strip() or "Detailed analysis unavailable",
            "risk_level": risk_level,
            "impact": impact.strip() or "Impact assessment needed",
            "recommendations": recommendations.strip() or "Manual review recommended"
        }
    
    def _format_recommendations(self, recommendations) -> str:
        """Format recommendations into a readable string"""
        if isinstance(recommendations, list):
            return "\n".join(f"• {rec}" for rec in recommendations)
        elif isinstance(recommendations, str):
            # Handle already formatted recommendations
            return recommendations
        else:
            return "Manual review recommended"
    
    def _analyze_intent(self, message: str) -> str:
        """Analyze user intent from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['alert', 'threat', 'suspicious', 'anomaly']):
            return "threat_analysis"
        elif any(word in message_lower for word in ['user', 'login', 'activity']):
            return "user_analysis"
        elif any(word in message_lower for word in ['ip', 'location', 'geography']):
            return "network_analysis"
        elif any(word in message_lower for word in ['help', 'how', 'what', 'explain']):
            return "general_help"
        else:
            return "general_query"
    
    def _generate_suggestions(self, intent: str, context: Optional[Dict] = None) -> List[str]:
        """Generate helpful suggestions based on intent"""
        suggestions = {
            "threat_analysis": [
                "Show me recent high-risk alerts",
                "Explain the latest anomaly",
                "What are the top threats today?"
            ],
            "user_analysis": [
                "Show me user behavior patterns",
                "Which users have the most alerts?",
                "Analyze login frequency trends"
            ],
            "network_analysis": [
                "Show me suspicious IP addresses",
                "Analyze geographic login patterns",
                "Check for VPN usage trends"
            ],
            "general_help": [
                "How does anomaly detection work?",
                "What metrics should I monitor?",
                "How to interpret risk scores?"
            ]
        }
        
        return suggestions.get(intent, [
            "Show me the security dashboard",
            "What should I be concerned about?",
            "How can I improve security?"
        ])


# Global instance
llm_service = LLMService()
