from ..models import License, SubscriptionPlan

class SubscriptionService:
    @staticmethod
    def get_feature_access(organization):
        """
        Returns a map of features allowed based on the organization's license.
        """
        try:
            license = organization.license
        except License.DoesNotExist:
            return cls._get_default_access()

        # Premium Plan enables all features
        if license.plan == SubscriptionPlan.PREMIUM:
            return {
                "full_automation": True,
                "gst_module": True,
                "compliance_drafts": True,
                "audit_intelligence": True,
                "max_businesses": 999
            }
        
        # Advanced Plan
        if license.plan == SubscriptionPlan.ADVANCED:
            return {
                "full_automation": False,
                "gst_module": True,
                "compliance_drafts": True,
                "audit_intelligence": False,
                "max_businesses": 20
            }

        # Basic Plan
        return {
            "full_automation": False,
            "gst_module": False,
            "compliance_drafts": False,
            "audit_intelligence": False,
            "max_businesses": 5
        }

    @staticmethod
    def _get_default_access():
        return {
            "full_automation": False,
            "gst_module": False,
            "compliance_drafts": False,
            "audit_intelligence": False,
            "max_businesses": 1
        }
