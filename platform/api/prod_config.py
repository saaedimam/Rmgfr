import os
from typing import Dict, Any

class ProductionConfig:
    def __init__(self):
        self.waf_rules = {
            "rate_limit_per_ip": 1000,  # requests per hour
            "max_request_size": 10 * 1024 * 1024,  # 10MB
            "blocked_headers": ["x-forwarded-for", "x-real-ip"],
            "allowed_origins": os.getenv("ALLOWED_ORIGINS", "").split(",")
        }
        
        self.backup_config = {
            "frequency": "daily",
            "retention_days": 30,
            "encryption": True,
            "pitr_enabled": True
        }
        
        self.pii_policies = {
            "retention_days": 90,
            "encryption_at_rest": True,
            "anonymization_after": 30
        }
    
    def get_waf_rules(self) -> Dict[str, Any]:
        return self.waf_rules
    
    def get_backup_config(self) -> Dict[str, Any]:
        return self.backup_config
    
    def get_pii_policies(self) -> Dict[str, Any]:
        return self.pii_policies

# Launch checklist
LAUNCH_CHECKLIST = [
    "✅ Environment variables configured",
    "✅ Database migrations applied",
    "✅ SSL certificates valid",
    "✅ Monitoring alerts configured",
    "✅ Backup procedures tested",
    "✅ Rollback procedures tested",
    "✅ Load testing completed",
    "✅ Security scan passed",
    "✅ Documentation updated",
    "✅ Team trained on procedures"
]
