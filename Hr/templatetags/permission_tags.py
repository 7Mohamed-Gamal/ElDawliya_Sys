from django import template
from administrator.utils import has_template_permission as utils_has_template_permission

register = template.Library()

@register.filter
def has_template_permission(user, template_path):
    """
    تحقق مما إذا كان المستخدم لديه صلاحية الوصول إلى قالب معين
    
    الاستخدام في القوالب:
    {% load permission_tags %}
    {% if user|has_template_permission:"Hr/reports/monthly_salary_report.html" %}
        <a href="{% url 'hr:monthly_salary_report' %}" class="btn btn-primary">عرض تقرير الرواتب الشهري</a>
    {% endif %}
    """
    return utils_has_template_permission(user, template_path)