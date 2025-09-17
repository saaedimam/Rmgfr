"""
Advanced Fraud Engine v2 - Real-time fraud detection
"""

import asyncio
import logging
import hashlib
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RiskFactor(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskAssessment:
    score: float
    factors: List[str]
    confidence: float
    recommendations: List[str]

class FraudEngine:
    """
    Advanced fraud detection engine with real-time processing
    """

    def __init__(self):
        self.risk_weights = {
            'velocity': 0.3,
            'device_anomaly': 0.25,
            'geolocation': 0.2,
            'behavioral': 0.15,
            'payment_risk': 0.1
        }

        # Known bad patterns
        self.bad_patterns = {
            'emails': [r'[a-zA-Z0-9._%+-]+@(test|fake|temp|spam)\.com'],
            'phones': [r'\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}'],  # Common test patterns
            'ips': [r'^192\.168\.', r'^10\.', r'^172\.(1[6-9]|2[0-9]|3[0-1])\.']  # Private IPs
        }

        # Device fingerprint patterns
        self.device_patterns = {
            'suspicious_user_agents': [
                'bot', 'crawler', 'spider', 'scraper', 'automated'
            ],
            'suspicious_browsers': [
                'headless', 'phantom', 'selenium', 'webdriver'
            ]
        }

    async def calculate_risk_score(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        profile_id: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        ip_address: Optional[str] = None,
        amount: Optional[float] = None,
        session_id: Optional[str] = None
    ) -> float:
        """
        Calculate comprehensive risk score for an event

        Args:
            event_type: Type of event (login, signup, payment, etc.)
            event_data: Event-specific data
            profile_id: User profile ID
            device_fingerprint: Device fingerprint hash
            ip_address: IP address
            amount: Transaction amount
            session_id: Session identifier

        Returns:
            Risk score between 0.0 (no risk) and 1.0 (high risk)
        """
        try:
            risk_factors = []
            total_score = 0.0

            # 1. Velocity Analysis
            velocity_score = await self._analyze_velocity(
                event_type, profile_id, ip_address, device_fingerprint
            )
            risk_factors.append(("velocity", velocity_score))
            total_score += velocity_score * self.risk_weights['velocity']

            # 2. Device Anomaly Detection
            device_score = await self._analyze_device_anomaly(
                device_fingerprint, event_data.get('user_agent', '')
            )
            risk_factors.append(("device_anomaly", device_score))
            total_score += device_score * self.risk_weights['device_anomaly']

            # 3. Geolocation Analysis
            geo_score = await self._analyze_geolocation(
                ip_address, profile_id, event_data
            )
            risk_factors.append(("geolocation", geo_score))
            total_score += geo_score * self.risk_weights['geolocation']

            # 4. Behavioral Analysis
            behavior_score = await self._analyze_behavior(
                event_type, event_data, profile_id, session_id
            )
            risk_factors.append(("behavioral", behavior_score))
            total_score += behavior_score * self.risk_weights['behavioral']

            # 5. Payment Risk Analysis
            payment_score = await self._analyze_payment_risk(
                event_type, amount, event_data, profile_id
            )
            risk_factors.append(("payment_risk", payment_score))
            total_score += payment_score * self.risk_weights['payment_risk']

            # Ensure score is between 0 and 1
            final_score = max(0.0, min(1.0, total_score))

            logger.debug(f"Risk calculation: {risk_factors}, final_score: {final_score}")

            return final_score

        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.5  # Default medium risk on error

    async def _analyze_velocity(
        self, event_type: str, profile_id: Optional[str],
        ip_address: Optional[str], device_fingerprint: Optional[str]
    ) -> float:
        """Analyze event velocity patterns"""
        try:
            # This would typically query a database for recent events
            # For now, we'll use simplified logic

            score = 0.0

            # High-frequency events from same IP
            if ip_address:
                # Check for rapid-fire events (simplified)
                if event_type in ['login', 'payment']:
                    # Simulate velocity check
                    recent_events = await self._get_recent_events_count(
                        ip_address=ip_address, minutes=5
                    )
                    if recent_events > 10:
                        score += 0.8
                    elif recent_events > 5:
                        score += 0.4

            # High-frequency events from same profile
            if profile_id:
                recent_profile_events = await self._get_recent_events_count(
                    profile_id=profile_id, minutes=10
                )
                if recent_profile_events > 20:
                    score += 0.9
                elif recent_profile_events > 10:
                    score += 0.5

            # Device velocity
            if device_fingerprint:
                recent_device_events = await self._get_recent_events_count(
                    device_fingerprint=device_fingerprint, minutes=15
                )
                if recent_device_events > 30:
                    score += 0.7
                elif recent_device_events > 15:
                    score += 0.3

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Error in velocity analysis: {e}")
            return 0.0

    async def _analyze_device_anomaly(
        self, device_fingerprint: Optional[str], user_agent: str
    ) -> float:
        """Analyze device anomalies"""
        try:
            score = 0.0

            # Check user agent for suspicious patterns
            user_agent_lower = user_agent.lower()
            for pattern in self.device_patterns['suspicious_user_agents']:
                if pattern in user_agent_lower:
                    score += 0.6

            for pattern in self.device_patterns['suspicious_browsers']:
                if pattern in user_agent_lower:
                    score += 0.8

            # Check for missing or invalid device fingerprint
            if not device_fingerprint:
                score += 0.3
            elif len(device_fingerprint) < 10:
                score += 0.2

            # Check for device fingerprint patterns
            if device_fingerprint:
                # Check for sequential or repeated patterns
                if self._is_sequential_fingerprint(device_fingerprint):
                    score += 0.4

                # Check for common test fingerprints
                if device_fingerprint in ['test', 'default', 'unknown']:
                    score += 0.7

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Error in device anomaly analysis: {e}")
            return 0.0

    async def _analyze_geolocation(
        self, ip_address: Optional[str], profile_id: Optional[str],
        event_data: Dict[str, Any]
    ) -> float:
        """Analyze geolocation patterns"""
        try:
            score = 0.0

            if not ip_address:
                return 0.0

            # Check for private/internal IPs
            for pattern in self.bad_patterns['ips']:
                if re.match(pattern, ip_address):
                    score += 0.5

            # Check for known VPN/Proxy IPs (simplified)
            if self._is_vpn_ip(ip_address):
                score += 0.3

            # Check for unusual geolocation changes
            if profile_id:
                # This would typically check against user's historical locations
                # For now, we'll use simplified logic
                recent_locations = await self._get_recent_locations(profile_id)
                if recent_locations and not self._is_location_consistent(ip_address, recent_locations):
                    score += 0.4

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Error in geolocation analysis: {e}")
            return 0.0

    async def _analyze_behavior(
        self, event_type: str, event_data: Dict[str, Any],
        profile_id: Optional[str], session_id: Optional[str]
    ) -> float:
        """Analyze behavioral patterns"""
        try:
            score = 0.0

            # Check for unusual event sequences
            if profile_id:
                recent_events = await self._get_recent_event_types(profile_id)
                if self._is_unusual_event_sequence(event_type, recent_events):
                    score += 0.3

            # Check for suspicious event data patterns
            if event_data:
                # Check for test data patterns
                for key, value in event_data.items():
                    if isinstance(value, str):
                        if any(pattern in value.lower() for pattern in ['test', 'fake', 'dummy']):
                            score += 0.4

                # Check for unusual data formats
                if 'email' in event_data:
                    email = event_data['email']
                    if any(re.match(pattern, email) for pattern in self.bad_patterns['emails']):
                        score += 0.6

            # Check for rapid session changes
            if session_id and profile_id:
                recent_sessions = await self._get_recent_sessions(profile_id)
                if len(recent_sessions) > 5:  # Multiple sessions in short time
                    score += 0.3

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Error in behavioral analysis: {e}")
            return 0.0

    async def _analyze_payment_risk(
        self, event_type: str, amount: Optional[float],
        event_data: Dict[str, Any], profile_id: Optional[str]
    ) -> float:
        """Analyze payment-specific risks"""
        try:
            score = 0.0

            if event_type != 'payment' or amount is None:
                return 0.0

            # Check for unusual amounts
            if amount <= 0:
                score += 0.8
            elif amount > 10000:  # High-value transaction
                score += 0.3
            elif amount < 1:  # Very small amount (potential test)
                score += 0.2

            # Check for round numbers (potential test transactions)
            if amount == int(amount) and amount in [1, 10, 100, 1000, 10000]:
                score += 0.1

            # Check for unusual payment patterns
            if profile_id:
                recent_payments = await self._get_recent_payment_amounts(profile_id)
                if recent_payments:
                    avg_amount = sum(recent_payments) / len(recent_payments)
                    if amount > avg_amount * 5:  # 5x average
                        score += 0.4

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Error in payment risk analysis: {e}")
            return 0.0

    def _is_sequential_fingerprint(self, fingerprint: str) -> bool:
        """Check if fingerprint appears sequential or generated"""
        # Simple check for sequential patterns
        if len(fingerprint) < 8:
            return False

        # Check for repeated characters
        if len(set(fingerprint)) < len(fingerprint) * 0.3:
            return True

        # Check for sequential patterns
        for i in range(len(fingerprint) - 3):
            if fingerprint[i:i+3].isdigit():
                try:
                    if int(fingerprint[i:i+3]) + 1 == int(fingerprint[i+1:i+4]):
                        return True
                except (ValueError, IndexError):
                    continue

        return False

    def _is_vpn_ip(self, ip_address: str) -> bool:
        """Check if IP is likely a VPN/Proxy (simplified)"""
        # This would typically use a VPN detection service
        # For now, we'll use simple heuristics
        vpn_patterns = [
            '10.0.0.', '172.16.', '192.168.',
            '127.0.0.', '0.0.0.0'
        ]

        for pattern in vpn_patterns:
            if ip_address.startswith(pattern):
                return True

        return False

    def _is_location_consistent(self, current_ip: str, recent_locations: List[str]) -> bool:
        """Check if current location is consistent with recent locations"""
        # Simplified location consistency check
        # In reality, this would use geolocation services
        return len(set(recent_locations)) <= 2  # Allow up to 2 different locations

    def _is_unusual_event_sequence(self, current_event: str, recent_events: List[str]) -> bool:
        """Check if current event is unusual given recent event sequence"""
        if not recent_events:
            return False

        # Check for rapid repeated events
        if len(recent_events) >= 3 and all(e == current_event for e in recent_events[-3:]):
            return True

        # Check for unusual sequences
        unusual_sequences = [
            ['signup', 'payment'],  # Payment immediately after signup
            ['login', 'login', 'login'],  # Multiple rapid logins
        ]

        for sequence in unusual_sequences:
            if recent_events[-len(sequence):] == sequence and current_event == sequence[-1]:
                return True

        return False

    # Mock database methods (in real implementation, these would query the database)
    async def _get_recent_events_count(self, **filters) -> int:
        """Get count of recent events matching filters"""
        # Mock implementation
        import random
        return random.randint(0, 50)

    async def _get_recent_locations(self, profile_id: str) -> List[str]:
        """Get recent locations for a profile"""
        # Mock implementation
        return ['US', 'CA'] if profile_id else []

    async def _get_recent_event_types(self, profile_id: str) -> List[str]:
        """Get recent event types for a profile"""
        # Mock implementation
        return ['login', 'view'] if profile_id else []

    async def _get_recent_sessions(self, profile_id: str) -> List[str]:
        """Get recent sessions for a profile"""
        # Mock implementation
        return ['session1', 'session2'] if profile_id else []

    async def _get_recent_payment_amounts(self, profile_id: str) -> List[float]:
        """Get recent payment amounts for a profile"""
        # Mock implementation
        return [50.0, 100.0, 25.0] if profile_id else []
