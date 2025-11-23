"""
Security Analysis Service
خدمة التحليل الأمني

This service provides comprehensive security analysis and threat detection
capabilities for the audit and monitoring system.
"""

import re
import json
import logging
from datetime import timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q

from ..models.audit import AuditLog, SecurityEvent, SystemMetric, Alert, AlertRule

User = get_user_model()
logger = logging.getLogger(__name__)


class SecurityAnalyzer:
    """
    Advanced security analysis and threat detection
    التحليل الأمني المتقدم واكتشاف التهديدات
    """
    
    def __init__(self):
        self.threat_patterns = self._load_threat_patterns()
        self.anomaly_thresholds = self._load_anomaly_thresholds()
        self.ip_reputation_cache = {}
    
    def analyze_request(self, audit_log, request, response) -> Optional[Dict[str, Any]]:
        """
        Analyze a request for security threats
        تحليل طلب للتهديدات الأمنية
        """
        threat_indicators = []
        
        # Analyze different threat vectors
        threat_indicators.extend(self._analyze_authentication_threats(audit_log, request, response))
        threat_indicators.extend(self._analyze_injection_attacks(audit_log, request))
        threat_indicators.extend(self._analyze_brute_force_attacks(audit_log))
        threat_indicators.extend(self._analyze_privilege_escalation(audit_log, request))
        threat_indicators.extend(self._analyze_data_exfiltration(audit_log, request, response))
        threat_indicators.extend(self._analyze_anomalous_behavior(audit_log))
        
        if not threat_indicators:
            return None
        
        # Calculate overall threat score
        threat_score = self._calculate_threat_score(threat_indicators)
        
        # Determine threat level
        threat_level = self._determine_threat_level(threat_score)
        
        if threat_level == 'info':
            return None  # Not significant enough to report
        
        return {
            'is_threat': True,
            'threat_type': self._determine_primary_threat_type(threat_indicators),
            'threat_level': threat_level,
            'threat_score': threat_score,
            'title': self._generate_threat_title(threat_indicators),
            'description': self._generate_threat_description(threat_indicators),
            'confidence': self._calculate_confidence(threat_indicators),
            'evidence': {
                'indicators': threat_indicators,
                'request_details': self._extract_request_details(request),
                'response_details': self._extract_response_details(response)
            }
        }
    
    def _analyze_authentication_threats(self, audit_log, request, response) -> List[Dict]:
        """
        Analyze authentication-related threats
        تحليل التهديدات المتعلقة بالمصادقة
        """
        indicators = []
        
        # Failed login detection
        if audit_log.action_type == 'login' and response.status_code >= 400:
            # Check for repeated failed logins from same IP
            recent_failures = AuditLog.objects.filter(
                ip_address=audit_log.ip_address,
                action_type='login',
                response_status__gte=400,
                timestamp__gte=timezone.now() - timedelta(minutes=15)
            ).count()
            
            if recent_failures >= 5:
                indicators.append({
                    'type': 'brute_force_login',
                    'severity': 'high',
                    'description': f'Multiple failed login attempts ({recent_failures}) from IP {audit_log.ip_address}',
                    'evidence': {'failed_attempts': recent_failures}
                })
            
            # Check for credential stuffing patterns
            if self._detect_credential_stuffing(audit_log):
                indicators.append({
                    'type': 'credential_stuffing',
                    'severity': 'high',
                    'description': 'Potential credential stuffing attack detected',
                    'evidence': {'pattern': 'multiple_usernames_same_ip'}
                })
        
        # Suspicious login patterns
        if audit_log.action_type == 'login' and response.status_code < 400:
            if self._detect_suspicious_login_pattern(audit_log):
                indicators.append({
                    'type': 'suspicious_login',
                    'severity': 'medium',
                    'description': 'Suspicious login pattern detected',
                    'evidence': self._get_login_pattern_evidence(audit_log)
                })
        
        return indicators
    
    def _analyze_injection_attacks(self, audit_log, request) -> List[Dict]:
        """
        Analyze for injection attacks (SQL, XSS, etc.)
        تحليل هجمات الحقن (SQL، XSS، إلخ)
        """
        indicators = []
        
        # SQL Injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
            r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
            r"('|\"|`).*(OR|AND).*(=|LIKE)",
            r"(--|#|/\*|\*/)",
        ]
        
        # XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
        ]
        
        # Check request data for malicious patterns
        request_data_str = json.dumps(audit_log.request_data, default=str).lower()
        
        for pattern in sql_patterns:
            if re.search(pattern, request_data_str, re.IGNORECASE):
                indicators.append({
                    'type': 'sql_injection',
                    'severity': 'high',
                    'description': 'Potential SQL injection attempt detected',
                    'evidence': {'pattern': pattern, 'matched_data': request_data_str[:200]}
                })
        
        for pattern in xss_patterns:
            if re.search(pattern, request_data_str, re.IGNORECASE):
                indicators.append({
                    'type': 'xss_attempt',
                    'severity': 'medium',
                    'description': 'Potential XSS attempt detected',
                    'evidence': {'pattern': pattern, 'matched_data': request_data_str[:200]}
                })
        
        return indicators
    
    def _analyze_brute_force_attacks(self, audit_log) -> List[Dict]:
        """
        Analyze for brute force attacks
        تحليل هجمات القوة الغاشمة
        """
        indicators = []
        
        # Check for rapid requests from same IP
        time_window = timezone.now() - timedelta(minutes=5)
        recent_requests = AuditLog.objects.filter(
            ip_address=audit_log.ip_address,
            timestamp__gte=time_window
        ).count()
        
        if recent_requests > 50:  # More than 50 requests in 5 minutes
            indicators.append({
                'type': 'brute_force_requests',
                'severity': 'high',
                'description': f'Excessive requests ({recent_requests}) from IP in 5 minutes',
                'evidence': {'request_count': recent_requests, 'time_window': '5_minutes'}
            })
        
        # Check for API brute force
        if audit_log.request_path.startswith('/api/'):
            api_requests = AuditLog.objects.filter(
                ip_address=audit_log.ip_address,
                request_path__startswith='/api/',
                timestamp__gte=time_window
            ).count()
            
            if api_requests > 30:  # More than 30 API requests in 5 minutes
                indicators.append({
                    'type': 'api_brute_force',
                    'severity': 'medium',
                    'description': f'Excessive API requests ({api_requests}) from IP',
                    'evidence': {'api_request_count': api_requests}
                })
        
        return indicators
    
    def _analyze_privilege_escalation(self, audit_log, request) -> List[Dict]:
        """
        Analyze for privilege escalation attempts
        تحليل محاولات تصعيد الصلاحيات
        """
        indicators = []
        
        # Check for admin access by non-admin users
        if '/admin/' in audit_log.request_path and audit_log.user:
            if not audit_log.user.is_staff and not audit_log.user.is_superuser:
                indicators.append({
                    'type': 'unauthorized_admin_access',
                    'severity': 'high',
                    'description': f'Non-admin user {audit_log.user.username} attempted admin access',
                    'evidence': {'user_id': audit_log.user.id, 'path': audit_log.request_path}
                })
        
        # Check for permission manipulation attempts
        if 'permission' in audit_log.request_path.lower() or 'role' in audit_log.request_path.lower():
            if audit_log.action_type in ['create', 'update', 'delete']:
                indicators.append({
                    'type': 'permission_manipulation',
                    'severity': 'high',
                    'description': 'Attempt to modify permissions or roles',
                    'evidence': {'action': audit_log.action_type, 'path': audit_log.request_path}
                })
        
        return indicators
    
    def _analyze_data_exfiltration(self, audit_log, request, response) -> List[Dict]:
        """
        Analyze for data exfiltration attempts
        تحليل محاولات تسريب البيانات
        """
        indicators = []
        
        # Check for bulk data exports
        if audit_log.action_type == 'export' or 'export' in audit_log.request_path:
            # Check export frequency
            recent_exports = AuditLog.objects.filter(
                user=audit_log.user,
                action_type='export',
                timestamp__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            if recent_exports > 5:  # More than 5 exports in 1 hour
                indicators.append({
                    'type': 'excessive_data_export',
                    'severity': 'medium',
                    'description': f'User performed {recent_exports} exports in 1 hour',
                    'evidence': {'export_count': recent_exports}
                })
        
        # Check for large response sizes (potential data dumps)
        response_size = len(getattr(response, 'content', b''))
        if response_size > 10 * 1024 * 1024:  # More than 10MB
            indicators.append({
                'type': 'large_data_response',
                'severity': 'low',
                'description': f'Large response size: {response_size} bytes',
                'evidence': {'response_size': response_size}
            })
        
        return indicators
    
    def _analyze_anomalous_behavior(self, audit_log) -> List[Dict]:
        """
        Analyze for anomalous user behavior
        تحليل السلوك الشاذ للمستخدم
        """
        indicators = []
        
        if not audit_log.user:
            return indicators
        
        # Check for unusual access times
        current_hour = audit_log.timestamp.hour
        if current_hour < 6 or current_hour > 22:  # Outside normal business hours
            # Check if user normally accesses system at this time
            normal_access = AuditLog.objects.filter(
                user=audit_log.user,
                timestamp__hour__range=(current_hour-1, current_hour+1),
                timestamp__gte=timezone.now() - timedelta(days=30)
            ).count()
            
            if normal_access < 3:  # Less than 3 times in past 30 days
                indicators.append({
                    'type': 'unusual_access_time',
                    'severity': 'low',
                    'description': f'User accessing system at unusual hour: {current_hour}:00',
                    'evidence': {'access_hour': current_hour, 'historical_access': normal_access}
                })
        
        # Check for unusual IP addresses
        user_ips = AuditLog.objects.filter(
            user=audit_log.user,
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).values_list('ip_address', flat=True).distinct()
        
        if audit_log.ip_address not in user_ips:
            indicators.append({
                'type': 'new_ip_address',
                'severity': 'low',
                'description': f'User accessing from new IP: {audit_log.ip_address}',
                'evidence': {'new_ip': audit_log.ip_address, 'known_ips': list(user_ips)}
            })
        
        return indicators
    
    def _detect_credential_stuffing(self, audit_log) -> bool:
        """
        Detect credential stuffing patterns
        اكتشاف أنماط حشو بيانات الاعتماد
        """
        # Check for multiple different usernames from same IP
        recent_logins = AuditLog.objects.filter(
            ip_address=audit_log.ip_address,
            action_type='login',
            timestamp__gte=timezone.now() - timedelta(minutes=30)
        ).values_list('request_data', flat=True)
        
        usernames = set()
        for login_data in recent_logins:
            if isinstance(login_data, dict) and 'username' in login_data:
                usernames.add(login_data['username'])
        
        return len(usernames) > 10  # More than 10 different usernames
    
    def _detect_suspicious_login_pattern(self, audit_log) -> bool:
        """
        Detect suspicious login patterns
        اكتشاف أنماط تسجيل الدخول المشبوهة
        """
        if not audit_log.user:
            return False
        
        # Check for rapid successive logins
        recent_logins = AuditLog.objects.filter(
            user=audit_log.user,
            action_type='login',
            response_status__lt=400,
            timestamp__gte=timezone.now() - timedelta(minutes=5)
        ).count()
        
        return recent_logins > 3  # More than 3 successful logins in 5 minutes
    
    def _get_login_pattern_evidence(self, audit_log) -> Dict:
        """
        Get evidence for suspicious login patterns
        الحصول على أدلة لأنماط تسجيل الدخول المشبوهة
        """
        return {
            'user_id': audit_log.user.id if audit_log.user else None,
            'ip_address': audit_log.ip_address,
            'user_agent': audit_log.user_agent[:100],
            'timestamp': audit_log.timestamp.isoformat()
        }
    
    def _calculate_threat_score(self, threat_indicators: List[Dict]) -> float:
        """
        Calculate overall threat score
        حساب درجة التهديد الإجمالية
        """
        severity_weights = {
            'low': 1,
            'medium': 3,
            'high': 7,
            'critical': 10
        }
        
        total_score = 0
        for indicator in threat_indicators:
            severity = indicator.get('severity', 'low')
            total_score += severity_weights.get(severity, 1)
        
        # Normalize score to 0-10 range
        max_possible_score = len(threat_indicators) * 10
        if max_possible_score > 0:
            normalized_score = (total_score / max_possible_score) * 10
        else:
            normalized_score = 0
        
        return min(normalized_score, 10)
    
    def _determine_threat_level(self, threat_score: float) -> str:
        """
        Determine threat level based on score
        تحديد مستوى التهديد بناءً على النتيجة
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
            return 'info'
    
    def _determine_primary_threat_type(self, threat_indicators: List[Dict]) -> str:
        """
        Determine primary threat type
        تحديد نوع التهديد الأساسي
        """
        if not threat_indicators:
            return 'suspicious_activity'
        
        # Count threat types
        threat_types = Counter(indicator['type'] for indicator in threat_indicators)
        
        # Return most common threat type
        return threat_types.most_common(1)[0][0]
    
    def _generate_threat_title(self, threat_indicators: List[Dict]) -> str:
        """
        Generate threat title
        توليد عنوان التهديد
        """
        primary_type = self._determine_primary_threat_type(threat_indicators)
        
        titles = {
            'brute_force_login': 'محاولة هجوم القوة الغاشمة على تسجيل الدخول',
            'credential_stuffing': 'محاولة حشو بيانات الاعتماد',
            'sql_injection': 'محاولة حقن SQL',
            'xss_attempt': 'محاولة هجوم XSS',
            'unauthorized_admin_access': 'محاولة وصول غير مصرح للإدارة',
            'permission_manipulation': 'محاولة التلاعب بالصلاحيات',
            'excessive_data_export': 'تصدير مفرط للبيانات',
            'suspicious_activity': 'نشاط مشبوه مكتشف'
        }
        
        return titles.get(primary_type, 'تهديد أمني مكتشف')
    
    def _generate_threat_description(self, threat_indicators: List[Dict]) -> str:
        """
        Generate threat description
        توليد وصف التهديد
        """
        descriptions = []
        for indicator in threat_indicators:
            descriptions.append(indicator.get('description', ''))
        
        return '; '.join(descriptions)
    
    def _calculate_confidence(self, threat_indicators: List[Dict]) -> float:
        """
        Calculate confidence score
        حساب درجة الثقة
        """
        # Base confidence on number and severity of indicators
        high_severity_count = sum(1 for i in threat_indicators if i.get('severity') == 'high')
        medium_severity_count = sum(1 for i in threat_indicators if i.get('severity') == 'medium')
        
        confidence = 0.3 + (high_severity_count * 0.3) + (medium_severity_count * 0.2)
        return min(confidence, 1.0)
    
    def _extract_request_details(self, request) -> Dict:
        """
        Extract relevant request details
        استخراج تفاصيل الطلب ذات الصلة
        """
        return {
            'method': request.method,
            'path': request.path,
            'content_type': getattr(request, 'content_type', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
            'referer': request.META.get('HTTP_REFERER', ''),
        }
    
    def _extract_response_details(self, response) -> Dict:
        """
        Extract relevant response details
        استخراج تفاصيل الاستجابة ذات الصلة
        """
        return {
            'status_code': response.status_code,
            'content_length': len(getattr(response, 'content', b'')),
            'content_type': response.get('Content-Type', ''),
        }
    
    def _load_threat_patterns(self) -> Dict:
        """
        Load threat detection patterns
        تحميل أنماط اكتشاف التهديدات
        """
        # This would typically load from configuration or database
        return {
            'sql_injection': [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
                r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
            ],
            'xss': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
            ]
        }
    
    def _load_anomaly_thresholds(self) -> Dict:
        """
        Load anomaly detection thresholds
        تحميل عتبات اكتشاف الشذوذ
        """
        return {
            'failed_login_threshold': 5,
            'request_rate_threshold': 50,
            'api_rate_threshold': 30,
            'export_frequency_threshold': 5,
        }


class ThreatIntelligence:
    """
    Threat intelligence and reputation service
    خدمة استخبارات التهديدات والسمعة
    """
    
    def __init__(self):
        self.reputation_cache_timeout = 3600  # 1 hour
    
    def check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """
        Check IP address reputation
        فحص سمعة عنوان IP
        """
        cache_key = f"ip_reputation_{ip_address}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # In a real implementation, this would query threat intelligence APIs
        reputation = {
            'is_malicious': False,
            'reputation_score': 0,  # 0-100, higher is worse
            'categories': [],
            'last_seen': None,
            'source': 'local_analysis'
        }
        
        # Simple local analysis
        if self._is_private_ip(ip_address):
            reputation['categories'].append('private')
        elif self._is_tor_exit_node(ip_address):
            reputation['categories'].append('tor')
            reputation['reputation_score'] = 30
        
        cache.set(cache_key, reputation, self.reputation_cache_timeout)
        return reputation
    
    def _is_private_ip(self, ip_address: str) -> bool:
        """Check if IP is in private range"""
        import ipaddress
        try:
            ip = ipaddress.ip_address(ip_address)
            return ip.is_private
        except ValueError:
            return False
    
    def _is_tor_exit_node(self, ip_address: str) -> bool:
        """Check if IP is a known Tor exit node"""
        # This would typically check against a Tor exit node list
        return False


class SecurityReporter:
    """
    Security reporting and alerting service
    خدمة التقارير والتنبيهات الأمنية
    """
    
    def generate_security_summary(self, start_date, end_date) -> Dict[str, Any]:
        """
        Generate security summary report
        توليد تقرير ملخص الأمان
        """
        # Get security events in date range
        security_events = SecurityEvent.objects.filter(
            detected_at__range=[start_date, end_date]
        )
        
        # Get audit logs in date range
        audit_logs = AuditLog.objects.filter(
            timestamp__range=[start_date, end_date]
        )
        
        # Calculate statistics
        total_events = security_events.count()
        critical_events = security_events.filter(threat_level='critical').count()
        high_events = security_events.filter(threat_level='high').count()
        
        failed_logins = audit_logs.filter(
            action_type='login',
            response_status__gte=400
        ).count()
        
        suspicious_activities = audit_logs.filter(is_suspicious=True).count()
        
        # Top threat sources
        top_ips = security_events.values('source_ip').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Threat trends
        daily_threats = security_events.extra(
            select={'day': 'date(detected_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        return {
            'summary': {
                'total_events': total_events,
                'critical_events': critical_events,
                'high_events': high_events,
                'failed_logins': failed_logins,
                'suspicious_activities': suspicious_activities,
            },
            'top_threat_sources': list(top_ips),
            'daily_trends': list(daily_threats),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }
    
    def generate_user_activity_report(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Generate user activity security report
        توليد تقرير أمان نشاط المستخدم
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        user_logs = AuditLog.objects.filter(
            user_id=user_id,
            timestamp__range=[start_date, end_date]
        )
        
        # Activity statistics
        total_activities = user_logs.count()
        suspicious_activities = user_logs.filter(is_suspicious=True).count()
        failed_operations = user_logs.filter(response_status__gte=400).count()
        
        # IP addresses used
        ip_addresses = user_logs.values('ip_address').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Activity by hour
        hourly_activity = user_logs.extra(
            select={'hour': 'extract(hour from timestamp)'}
        ).values('hour').annotate(count=Count('id')).order_by('hour')
        
        # Security events targeting this user
        security_events = SecurityEvent.objects.filter(
            target_user_id=user_id,
            detected_at__range=[start_date, end_date]
        )
        
        return {
            'user_id': user_id,
            'period_days': days,
            'activity_summary': {
                'total_activities': total_activities,
                'suspicious_activities': suspicious_activities,
                'failed_operations': failed_operations,
                'security_events': security_events.count(),
            },
            'ip_addresses': list(ip_addresses),
            'hourly_activity': list(hourly_activity),
            'security_events': [
                {
                    'id': str(event.id),
                    'event_type': event.event_type,
                    'threat_level': event.threat_level,
                    'title': event.title,
                    'detected_at': event.detected_at.isoformat()
                }
                for event in security_events[:10]
            ]
        }