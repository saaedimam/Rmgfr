"""
Centralized validation schemas using Pydantic
Crystallizes validation logic into clear, reusable models
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from enum import Enum
import re

class EventType(str, Enum):
    LOGIN = "login"
    SIGNUP = "signup"
    CHECKOUT = "checkout"
    PAYMENT = "payment"
    CUSTOM = "custom"

class RiskBand(str, Enum):
    LOW = "low"
    MED = "med"
    HIGH = "high"
    CRITICAL = "critical"

class DecisionAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"
    STEP_UP = "step_up"

class CustomerSegment(str, Enum):
    NEW_USER = "new_user"
    RETURNING = "returning"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class EventCreateSchema(BaseModel):
    """Schema for event creation with comprehensive validation"""
    event_type: EventType = Field(..., description="Type of event")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    profile_id: Optional[str] = Field(None, description="External profile ID")
    session_id: Optional[str] = Field(None, description="Session identifier")
    device_fingerprint: Optional[str] = Field(None, description="Device fingerprint hash")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    amount: Optional[float] = Field(None, ge=0, description="Transaction amount")
    currency: Optional[str] = Field(None, description="Currency code")

    @validator('profile_id')
    def validate_profile_id(cls, v):
        if v is not None and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Profile ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @validator('session_id')
    def validate_session_id(cls, v):
        if v is not None and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Session ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @validator('device_fingerprint')
    def validate_device_fingerprint(cls, v):
        if v is not None and not re.match(r'^[a-f0-9]{32,64}$', v):
            raise ValueError('Device fingerprint must be a valid hash (32-64 hex characters)')
        return v

    @validator('ip_address')
    def validate_ip_address(cls, v):
        if v is not None:
            # Basic IP validation (IPv4 and IPv6)
            ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'

            if not (re.match(ipv4_pattern, v) or re.match(ipv6_pattern, v)):
                raise ValueError('IP address must be a valid IPv4 or IPv6 address')
        return v

    @validator('currency')
    def validate_currency(cls, v):
        if v is not None and not re.match(r'^[A-Z]{3}$', v):
            raise ValueError('Currency must be a valid 3-letter ISO code')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v

    @root_validator
    def validate_payment_event(cls, values):
        """Validate payment-specific fields"""
        event_type = values.get('event_type')
        amount = values.get('amount')
        currency = values.get('currency')

        if event_type == EventType.PAYMENT:
            if amount is None:
                raise ValueError('Amount is required for payment events')
            if currency is None:
                raise ValueError('Currency is required for payment events')

        return values

class RiskThresholdsSchema(BaseModel):
    """Schema for risk threshold validation"""
    low: float = Field(..., ge=0, le=1, description="Low risk threshold")
    medium: float = Field(..., ge=0, le=1, description="Medium risk threshold")
    high: float = Field(..., ge=0, le=1, description="High risk threshold")
    critical: float = Field(..., ge=0, le=1, description="Critical risk threshold")

    @root_validator
    def validate_threshold_ordering(cls, values):
        """Validate that thresholds are in ascending order"""
        low = values.get('low', 0)
        medium = values.get('medium', 0)
        high = values.get('high', 0)
        critical = values.get('critical', 0)

        if not (low < medium < high < critical):
            raise ValueError('Risk thresholds must be in ascending order: low < medium < high < critical')

        return values

class VelocityLimitsSchema(BaseModel):
    """Schema for velocity limits validation"""
    max_events_per_minute: int = Field(..., ge=1, description="Maximum events per minute")
    max_events_per_hour: int = Field(..., ge=1, description="Maximum events per hour")
    max_events_per_day: int = Field(..., ge=1, description="Maximum events per day")

    @root_validator
    def validate_velocity_ordering(cls, values):
        """Validate that velocity limits are in ascending order"""
        per_minute = values.get('max_events_per_minute', 0)
        per_hour = values.get('max_events_per_hour', 0)
        per_day = values.get('max_events_per_day', 0)

        if not (per_minute <= per_hour <= per_day):
            raise ValueError('Velocity limits must be in ascending order: per_minute <= per_hour <= per_day')

        return values

class PaymentSettingsSchema(BaseModel):
    """Schema for payment settings validation"""
    max_amount: float = Field(..., gt=0, description="Maximum payment amount")
    min_amount: float = Field(..., ge=0, description="Minimum payment amount")
    suspicious_amounts: List[float] = Field(default_factory=list, description="Suspicious amount values")
    enable_round_number_detection: bool = Field(default=True, description="Enable round number detection")

    @validator('suspicious_amounts')
    def validate_suspicious_amounts(cls, v, values):
        """Validate suspicious amounts are within valid range"""
        max_amount = values.get('max_amount', 0)
        min_amount = values.get('min_amount', 0)

        for amount in v:
            if amount < min_amount or amount > max_amount:
                raise ValueError(f'Suspicious amount {amount} must be between {min_amount} and {max_amount}')

        return v

    @root_validator
    def validate_amount_range(cls, values):
        """Validate amount range"""
        max_amount = values.get('max_amount', 0)
        min_amount = values.get('min_amount', 0)

        if min_amount >= max_amount:
            raise ValueError('Minimum amount must be less than maximum amount')

        return values

class NotificationSettingsSchema(BaseModel):
    """Schema for notification settings validation"""
    email_alerts: bool = Field(default=True, description="Enable email alerts")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")
    alert_threshold: float = Field(..., ge=0, le=1, description="Alert threshold")

    @validator('webhook_url')
    def validate_webhook_url(cls, v):
        if v is not None and v.strip():
            # Basic URL validation
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(url_pattern, v):
                raise ValueError('Webhook URL must be a valid HTTP/HTTPS URL')
        return v

class FraudSettingsSchema(BaseModel):
    """Comprehensive fraud settings validation schema"""
    enabled: bool = Field(default=True, description="Enable fraud detection")
    risk_thresholds: RiskThresholdsSchema = Field(..., description="Risk thresholds")
    velocity_limits: VelocityLimitsSchema = Field(..., description="Velocity limits")
    payment_settings: PaymentSettingsSchema = Field(..., description="Payment settings")
    notification_settings: NotificationSettingsSchema = Field(..., description="Notification settings")

    class Config:
        extra = "forbid"  # Prevent additional fields

class RuleDefinitionSchema(BaseModel):
    """Schema for rule definition validation"""
    name: str = Field(..., min_length=1, max_length=100, description="Rule name")
    rule_type: str = Field(..., description="Type of rule")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Rule conditions")
    action: DecisionAction = Field(..., description="Rule action")
    priority: int = Field(default=0, ge=0, le=100, description="Rule priority")
    enabled: bool = Field(default=True, description="Rule enabled status")
    description: str = Field(default="", max_length=500, description="Rule description")

    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\s-]+$', v):
            raise ValueError('Rule name must contain only alphanumeric characters, spaces, hyphens, and underscores')
        return v

    @validator('rule_type')
    def validate_rule_type(cls, v):
        allowed_types = ['rate_limit', 'velocity', 'device', 'custom', 'geolocation', 'behavior']
        if v not in allowed_types:
            raise ValueError(f'Rule type must be one of: {allowed_types}')
        return v

class DecisionMatrixEntrySchema(BaseModel):
    """Schema for decision matrix entry validation"""
    event_type: EventType = Field(..., description="Event type")
    risk_band: RiskBand = Field(..., description="Risk band")
    customer_segment: CustomerSegment = Field(..., description="Customer segment")
    action: DecisionAction = Field(..., description="Decision action")
    max_fpr: float = Field(..., ge=0, le=1, description="Maximum false positive rate")
    confidence_threshold: float = Field(..., ge=0, le=1, description="Confidence threshold")
    notes: str = Field(default="", max_length=500, description="Notes")

class ValidationError(BaseModel):
    """Schema for validation error responses"""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    value: Any = Field(None, description="Value that failed validation")

class ValidationResult(BaseModel):
    """Schema for validation result responses"""
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: List[ValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")

def validate_event_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate event data using the schema"""
    try:
        EventCreateSchema(**data)
        return ValidationResult(is_valid=True)
    except Exception as e:
        if hasattr(e, 'errors'):
            errors = [
                ValidationError(
                    field=".".join(str(x) for x in error['loc']),
                    message=error['msg'],
                    value=error.get('input')
                )
                for error in e.errors()
            ]
        else:
            errors = [ValidationError(field="root", message=str(e))]

        return ValidationResult(is_valid=False, errors=errors)

def validate_fraud_settings(data: Dict[str, Any]) -> ValidationResult:
    """Validate fraud settings using the schema"""
    try:
        FraudSettingsSchema(**data)
        return ValidationResult(is_valid=True)
    except Exception as e:
        if hasattr(e, 'errors'):
            errors = [
                ValidationError(
                    field=".".join(str(x) for x in error['loc']),
                    message=error['msg'],
                    value=error.get('input')
                )
                for error in e.errors()
            ]
        else:
            errors = [ValidationError(field="root", message=str(e))]

        return ValidationResult(is_valid=False, errors=errors)
