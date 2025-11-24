"""
Advanced Threat Detection and Monitoring Service
خدمة اكتشاف ومراقبة التهديدات المتقدمة

This service provides real-time threat detection, behavioral analysis,
and automated response capabilities for security incidents.
"""

import re
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q

from ..models.audit import AuditLog, SecurityEvent, Alert, AlertRule

User = get_user_model()
logger = logging.getLogger(__name__)


@dataclass
class ThreatSignature:
    """
    Threat signature for pattern matching
    توقيع التهديد لمطابقة الأنماط
    """
    name: str
    pattern: str
    threat_type: str
    severity: str
    description: str
    confidence: float = 0.8


@dataclass
class BehaviorProfile:
    """
    User behavior profile for anomaly detection
    ملف السلوك للمستخدم لاكتشاف الشذوذ
    """
    user_id: int
    normal_login_hours: List[int]
    normal_ip_ranges: List[str]
    typical_actions: Dict[str, int]
    average_session_duration: float
    common_user_agents: List[str]
    last_updated: datetime


class ThreatDetectionEngine:
    """
    Advanced threat detection engine
    محرك اكتشاف التهديدات المتقدم
    """

    def __init__(self):
        """__init__ function"""
        self.threat_signatures = self._load_threat_signatures()
        self.behavior_profiles = {}
        self.attack_patterns = self._load_attack_patterns()
        self.suspicious_activities = deque(maxlen=1000)

    def _load_threat_signatures(self) -> List[ThreatSignature]:
        """
        Load threat signatures for pattern matching
        تحميل توقيعات التهديدات لمطابقة الأنماط
        """
        return [
            # SQL Injection signatures
            ThreatSignature(
                name="SQL Injection - Union Attack",
                pattern=r"(?i)(union\s+select|union\s+all\s+select)",
                threat_type="sql_injection",
                severity="high",
                description="SQL injection attempt using UNION operator"
            ),
            ThreatSignature(
                name="SQL Injection - Boolean Blind",
                pattern=r"(?i)(and\s+\d+\s*=\s*\d+|or\s+\d+\s*=\s*\d+)",
                threat_type="sql_injection",
                severity="medium",
                description="Boolean-based blind SQL injection attempt"
            ),
            ThreatSignature(
                name="SQL Injection - Time Blind",
                pattern=r"(?i)(sleep\s*\(|waitfor\s+delay|benchmark\s*\()",
                threat_type="sql_injection",
                severity="high",
                description="Time-based blind SQL injection attempt"
            ),

            # XSS signatures
            ThreatSignature(
                name="XSS - Script Tag",
                pattern=r"(?i)<script[^>]*>.*?</script>",
                threat_type="xss",
                severity="medium",
                description="Cross-site scripting attempt using script tags"
            ),
            ThreatSignature(
                name="XSS - Event Handler",
                pattern=r"(?i)on\w+\s*=\s*[\"']?[^\"'>]*[\"']?",
                threat_type="xss",
                severity="medium",
                description="XSS attempt using event handlers"
            ),
            ThreatSignature(
                name="XSS - JavaScript Protocol",
                pattern=r"(?i)javascript\s*:",
                threat_type="xss",
                severity="medium",
                description="XSS attempt using javascript protocol"
            ),

            # Path Traversal signatures
            ThreatSignature(
                name="Path Traversal - Directory Traversal",
                pattern=r"(\.\./|\.\.\\\|%2e%2e%2f|%2e%2e%5c)",
                threat_type="path_traversal",
                severity="high",
                description="Directory traversal attempt"
            ),
            ThreatSignature(
                name="Path Traversal - System Files",
                pattern=r"(?i)(etc/passwd|boot\.ini|win\.ini|system32)",
                threat_type="path_traversal",
                severity="critical",
                description="Attempt to access system files"
            ),

            # Command Injection signatures
            ThreatSignature(
                name="Command Injection - Shell Commands",
                pattern=r"(?i)(;|\||\&)\s*(ls|dir|cat|type|whoami|id|uname)",
                threat_type="command_injection",
                severity="critical",
                description="Command injection attempt"
            ),

            # LDAP Injection signatures
            ThreatSignature(
                name="LDAP Injection",
                pattern=r"(\*\)|\(\||\)\(|\(\&)",
                threat_type="ldap_injection",
                severity="medium",
                description="LDAP injection attempt"
            ),

            # XXE signatures
            ThreatSignature(
                name="XXE - External Entity",
                pattern=r"(?i)<!entity.*system|<!entity.*public",
                threat_type="xxe",
                severity="high",
                description="XML External Entity (XXE) attack attempt"
            ),
        ]

    def _load_attack_patterns(self) -> Dict[str, List[str]]:
        """
        Load known attack patterns
        تحميل أنماط الهجمات المعروفة
        """
        return {
            'brute_force_indicators': [
                'multiple_failed_logins',
                'rapid_login_attempts',
                'dictionary_usernames',
                'common_passwords'
            ],
            'reconnaissance_indicators': [
                'directory_enumeration',
                'port_scanning',
                'vulnerability_scanning',
                'information_gathering'
            ],
            'privilege_escalation_indicators': [
                'admin_access_attempts',
                'permission_manipulation',
                'role_elevation_attempts',
                'unauthorized_api_access'
            ],
            'data_exfiltration_indicators': [
                'bulk_data_access',
                'unusual_download_patterns',
                'off_hours_access',
                'large_response_sizes'
            ]
        }

    def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze request for threats
        تحليل الطلب للتهديدات
        """
        threats_detected = []

        # Pattern-based detection
        pattern_threats = self._detect_pattern_threats(request_data)
        threats_detected.extend(pattern_threats)

        # Behavioral analysis
        if request_data.get('user_id'):
            behavioral_threats = self._detect_behavioral_anomalies(request_data)
            threats_detected.extend(behavioral_threats)

        # Rate-based detection
        rate_threats = self._detect_rate_based_threats(request_data)
        threats_detected.extend(rate_threats)

        # Correlation analysis
        correlation_threats = self._detect_correlated_threats(request_data)
        threats_detected.extend(correlation_threats)

        # Calculate overall threat score
        threat_score = self._calculate_threat_score(threats_detected)

        return {
            'threats_detected': threats_detected,
            'threat_score': threat_score,
            'risk_level': self._determine_risk_level(threat_score),
            'recommended_actions': self._get_recommended_actions(threats_detected)
        }

    def _detect_pattern_threats(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect threats using signature patterns
        اكتشاف التهديدات باستخدام أنماط التوقيع
        """
        threats = []

        # Combine all request data for analysis
        analysis_text = ' '.join([
            str(request_data.get('url', '')),
            str(request_data.get('query_string', '')),
            str(request_data.get('post_data', '')),
            str(request_data.get('headers', {}))
        ]).lower()

        for signature in self.threat_signatures:
            if re.search(signature.pattern, analysis_text):
                threats.append({
                    'type': 'pattern_match',
                    'signature_name': signature.name,
                    'threat_type': signature.threat_type,
                    'severity': signature.severity,
                    'confidence': signature.confidence,
                    'description': signature.description,
                    'matched_pattern': signature.pattern
                })

        return threats

    def _detect_behavioral_anomalies(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect behavioral anomalies
        اكتشاف الشذوذ السلوكي
        """
        threats = []
        user_id = request_data.get('user_id')

        if not user_id:
            return threats

        # Get or create behavior profile
        profile = self._get_behavior_profile(user_id)

        if not profile:
            return threats

        # Check login time anomaly
        current_hour = datetime.now().hour
        if current_hour not in profile.normal_login_hours:
            threats.append({
                'type': 'behavioral_anomaly',
                'anomaly_type': 'unusual_login_time',
                'severity': 'low',
                'confidence': 0.6,
                'description': f'Login at unusual hour: {current_hour}',
                'details': {
                    'current_hour': current_hour,
                    'normal_hours': profile.normal_login_hours
                }
            })

        # Check IP address anomaly
        current_ip = request_data.get('ip_address')
        if current_ip and not self._is_ip_in_normal_ranges(current_ip, profile.normal_ip_ranges):
            threats.append({
                'type': 'behavioral_anomaly',
                'anomaly_type': 'unusual_ip_address',
                'severity': 'medium',
                'confidence': 0.7,
                'description': f'Access from unusual IP: {current_ip}',
                'details': {
                    'current_ip': current_ip,
                    'normal_ranges': profile.normal_ip_ranges
                }
            })

        # Check action frequency anomaly
        action = request_data.get('action')
        if action:
            normal_frequency = profile.typical_actions.get(action, 0)
            current_frequency = self._get_recent_action_frequency(user_id, action)

            if current_frequency > normal_frequency * 3:  # 3x normal frequency
                threats.append({
                    'type': 'behavioral_anomaly',
                    'anomaly_type': 'unusual_action_frequency',
                    'severity': 'medium',
                    'confidence': 0.8,
                    'description': f'Unusual frequency for action: {action}',
                    'details': {
                        'action': action,
                        'current_frequency': current_frequency,
                        'normal_frequency': normal_frequency
                    }
                })

        return threats

    def _detect_rate_based_threats(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect rate-based threats
        اكتشاف التهديدات القائمة على المعدل
        """
        threats = []

        ip_address = request_data.get('ip_address')
        user_id = request_data.get('user_id')

        # Check request rate from IP
        if ip_address:
            ip_rate = self._get_request_rate(f"ip_{ip_address}", 60)  # requests per minute
            if ip_rate > 100:  # More than 100 requests per minute
                threats.append({
                    'type': 'rate_based',
                    'threat_type': 'high_request_rate',
                    'severity': 'medium',
                    'confidence': 0.9,
                    'description': f'High request rate from IP: {ip_rate} req/min',
                    'details': {'ip_address': ip_address, 'rate': ip_rate}
                })

        # Check failed login rate
        if request_data.get('action') == 'login' and request_data.get('status') == 'failed':
            failed_rate = self._get_failed_login_rate(ip_address, 300)  # 5 minutes
            if failed_rate > 10:
                threats.append({
                    'type': 'rate_based',
                    'threat_type': 'brute_force_login',
                    'severity': 'high',
                    'confidence': 0.95,
                    'description': f'Brute force login attempt: {failed_rate} failures',
                    'details': {'ip_address': ip_address, 'failed_attempts': failed_rate}
                })

        return threats

    def _detect_correlated_threats(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect threats through correlation analysis
        اكتشاف التهديدات من خلال تحليل الارتباط
        """
        threats = []

        # Add current activity to suspicious activities queue
        self.suspicious_activities.append({
            'timestamp': timezone.now(),
            'ip_address': request_data.get('ip_address'),
            'user_id': request_data.get('user_id'),
            'action': request_data.get('action'),
            'url': request_data.get('url')
        })

        # Look for attack patterns in recent activities
        recent_activities = [
            activity for activity in self.suspicious_activities
            if timezone.now() - activity['timestamp'] < timedelta(minutes=10)
        ]

        # Check for reconnaissance patterns
        if self._detect_reconnaissance_pattern(recent_activities):
            threats.append({
                'type': 'correlated',
                'threat_type': 'reconnaissance',
                'severity': 'medium',
                'confidence': 0.8,
                'description': 'Reconnaissance activity pattern detected',
                'details': {'activity_count': len(recent_activities)}
            })

        # Check for privilege escalation patterns
        if self._detect_privilege_escalation_pattern(recent_activities):
            threats.append({
                'type': 'correlated',
                'threat_type': 'privilege_escalation',
                'severity': 'high',
                'confidence': 0.85,
                'description': 'Privilege escalation pattern detected',
                'details': {'activity_count': len(recent_activities)}
            })

        return threats

    def _get_behavior_profile(self, user_id: int) -> Optional[BehaviorProfile]:
        """
        Get or create behavior profile for user
        الحصول على أو إنشاء ملف السلوك للمستخدم
        """
        cache_key = f"behavior_profile_{user_id}"
        profile = cache.get(cache_key)

        if profile:
            return profile

        # Build profile from historical data
        profile = self._build_behavior_profile(user_id)

        if profile:
            cache.set(cache_key, profile, 3600)  # Cache for 1 hour

        return profile

    def _build_behavior_profile(self, user_id: int) -> Optional[BehaviorProfile]:
        """
        Build behavior profile from historical audit data
        بناء ملف السلوك من بيانات التدقيق التاريخية
        """
        # Get last 30 days of user activity
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        user_logs = AuditLog.objects.filter(
            user_id=user_id,
            timestamp__range=[start_date, end_date]
        )

        if user_logs.count() < 10:  # Need minimum activity for profiling
            return None

        # Analyze login hours
        login_logs = user_logs.filter(action_type='login')
        normal_login_hours = list(set(
            log.timestamp.hour for log in login_logs
        ))

        # Analyze IP ranges
        ip_addresses = list(set(
            log.ip_address for log in user_logs if log.ip_address
        ))
        normal_ip_ranges = self._extract_ip_ranges(ip_addresses)

        # Analyze typical actions
        action_counts = {}
        for log in user_logs:
            action_counts[log.action_type] = action_counts.get(log.action_type, 0) + 1

        # Calculate average session duration (simplified)
        session_durations = []
        # This would need more complex logic to track actual sessions
        average_session_duration = 1800  # Default 30 minutes

        # Analyze user agents
        user_agents = list(set(
            log.user_agent for log in user_logs if log.user_agent
        ))[:5]  # Keep top 5

        return BehaviorProfile(
            user_id=user_id,
            normal_login_hours=normal_login_hours,
            normal_ip_ranges=normal_ip_ranges,
            typical_actions=action_counts,
            average_session_duration=average_session_duration,
            common_user_agents=user_agents,
            last_updated=timezone.now()
        )

    def _extract_ip_ranges(self, ip_addresses: List[str]) -> List[str]:
        """
        Extract IP ranges from list of IP addresses
        استخراج نطاقات IP من قائمة عناوين IP
        """
        ranges = []

        for ip in ip_addresses:
            try:
                import ipaddress
                # Create /24 subnet for each IP
                network = ipaddress.ip_network(f"{ip}/24", strict=False)
                ranges.append(str(network))
            except ValueError:
                continue

        return list(set(ranges))

    def _is_ip_in_normal_ranges(self, ip_address: str, normal_ranges: List[str]) -> bool:
        """
        Check if IP address is in normal ranges
        التحقق من كون عنوان IP في النطاقات العادية
        """
        try:
            import ipaddress
            ip = ipaddress.ip_address(ip_address)

            for range_str in normal_ranges:
                network = ipaddress.ip_network(range_str)
                if ip in network:
                    return True
        except ValueError:
            pass

        return False

    def _get_recent_action_frequency(self, user_id: int, action: str) -> int:
        """
        Get recent frequency of specific action for user
        الحصول على تكرار حديث لإجراء معين للمستخدم
        """
        cache_key = f"action_freq_{user_id}_{action}"
        frequency = cache.get(cache_key, 0)

        # Increment and cache
        cache.set(cache_key, frequency + 1, 3600)  # 1 hour window

        return frequency + 1

    def _get_request_rate(self, identifier: str, window_seconds: int) -> int:
        """
        Get request rate for identifier within time window
        الحصول على معدل الطلبات للمعرف خلال نافزة زمنية
        """
        cache_key = f"rate_{identifier}_{window_seconds}"
        current_count = cache.get(cache_key, 0)

        # Increment counter
        cache.set(cache_key, current_count + 1, window_seconds)

        return current_count + 1

    def _get_failed_login_rate(self, ip_address: str, window_seconds: int) -> int:
        """
        Get failed login rate for IP address
        الحصول على معدل فشل تسجيل الدخول لعنوان IP
        """
        cache_key = f"failed_login_{ip_address}_{window_seconds}"
        current_count = cache.get(cache_key, 0)

        # Increment counter
        cache.set(cache_key, current_count + 1, window_seconds)

        return current_count + 1

    def _detect_reconnaissance_pattern(self, activities: List[Dict]) -> bool:
        """
        Detect reconnaissance activity patterns
        اكتشاف أنماط نشاط الاستطلاع
        """
        # Look for directory enumeration patterns
        urls = [activity.get('url', '') for activity in activities]

        # Check for systematic URL probing
        unique_paths = set()
        for url in urls:
            if url:
                path = url.split('?')[0]  # Remove query string
                unique_paths.add(path)

        # If accessing many different paths rapidly, might be reconnaissance
        return len(unique_paths) > 20

    def _detect_privilege_escalation_pattern(self, activities: List[Dict]) -> bool:
        """
        Detect privilege escalation patterns
        اكتشاف أنماط تصعيد الصلاحيات
        """
        # Look for admin/permission related actions
        admin_actions = [
            activity for activity in activities
            if any(keyword in str(activity.get('url', '')).lower()
                  for keyword in ['admin', 'permission', 'role', 'user'])
        ]

        # If many admin-related actions in short time, might be privilege escalation
        return len(admin_actions) > 5

    def _calculate_threat_score(self, threats: List[Dict[str, Any]]) -> float:
        """
        Calculate overall threat score
        حساب درجة التهديد الإجمالية
        """
        if not threats:
            return 0.0

        severity_weights = {
            'low': 1,
            'medium': 3,
            'high': 7,
            'critical': 10
        }

        total_score = 0
        for threat in threats:
            severity = threat.get('severity', 'low')
            confidence = threat.get('confidence', 0.5)
            weight = severity_weights.get(severity, 1)

            total_score += weight * confidence

        # Normalize to 0-10 scale
        max_possible = len(threats) * 10
        normalized_score = (total_score / max_possible) * 10 if max_possible > 0 else 0

        return min(normalized_score, 10.0)

    def _determine_risk_level(self, threat_score: float) -> str:
        """
        Determine risk level based on threat score
        تحديد مستوى المخاطر بناءً على درجة التهديد
        """
        if threat_score >= 8:
            return 'critical'
        elif threat_score >= 6:
            return 'high'
        elif threat_score >= 3:
            return 'medium'
        elif threat_score >= 1:
            return 'low'
        else:
            return 'minimal'

    def _get_recommended_actions(self, threats: List[Dict[str, Any]]) -> List[str]:
        """
        Get recommended actions based on detected threats
        الحصول على الإجراءات الموصى بها بناءً على التهديدات المكتشفة
        """
        actions = []

        threat_types = set(threat.get('threat_type', '') for threat in threats)

        if 'sql_injection' in threat_types:
            actions.append('Block request and review input validation')

        if 'xss' in threat_types:
            actions.append('Sanitize input and review output encoding')

        if 'brute_force_login' in threat_types:
            actions.append('Implement account lockout and CAPTCHA')

        if 'reconnaissance' in threat_types:
            actions.append('Monitor for follow-up attacks and consider IP blocking')

        if 'privilege_escalation' in threat_types:
            actions.append('Review user permissions and audit access controls')

        if not actions:
            actions.append('Continue monitoring')

        return actions


# Global instance
threat_detection_engine = ThreatDetectionEngine()
