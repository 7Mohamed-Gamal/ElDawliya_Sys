class ReportService:
    def __init__(self, user):
        self.user = user
    
    def can_generate_report(self, report_type):
        return has_report_permission(self.user, report_type)
        
    def generate_report(self, report_type, **kwargs):
        if not self.can_generate_report(report_type):
            raise PermissionDenied
            
        # ...existing code...
        
    def export_report(self, report_type, format='pdf', **kwargs):
        if not has_export_permission(self.user, report_type):
            raise PermissionDenied
            
        # ...existing code...