from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from administrator.models import Department, Module, Permission
from Hr.decorators import MODULES, DEPARTMENT_NAME

User = get_user_model()

class HrPermissionsTestCase(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpassword',
            Role='admin'
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            password='userpassword',
            Role='user'
        )
        
        # Create HR department
        self.hr_department = Department.objects.create(
            name=DEPARTMENT_NAME,
            description='قسم الموارد البشرية',
            icon='fas fa-user-tie',
            url_name='hr',
            order=1,
            is_active=True,
        )
        
        # Create HR modules
        self.modules = {}
        for module_key, module_name in MODULES.items():
            module = Module.objects.create(
                department=self.hr_department,
                name=module_name,
                description=f'وحدة {module_name}',
                url_name=module_key,
                order=list(MODULES.keys()).index(module_key) + 1,
                is_active=True,
            )
            self.modules[module_key] = module
        
        # Create permissions for each module
        self.permissions = {}
        for module_key, module in self.modules.items():
            module_perms = {}
            for perm_type in ['view', 'add', 'edit', 'delete', 'print']:
                perm = Permission.objects.create(
                    module=module,
                    permission_type=perm_type,
                    description=f'صلاحية {perm_type} لوحدة {module.name}',
                )
                module_perms[perm_type] = perm
            self.permissions[module_key] = module_perms
        
        # Create HR group
        self.hr_group = Group.objects.create(name='HR Staff')
        
        # Add view permissions for employees to HR group
        self.hr_group.adminpermission_set.add(self.permissions['employees']['view'])
        
        # Add regular user to HR group
        self.regular_user.groups.add(self.hr_group)
        
        # Create clients
        self.admin_client = Client()
        self.admin_client.login(username='admin', password='adminpassword')
        
        self.user_client = Client()
        self.user_client.login(username='user', password='userpassword')
        
        self.anonymous_client = Client()
    
    def test_admin_can_access_all_hr_pages(self):
        """Test that admin users can access all HR pages"""
        # Test employee list
        response = self.admin_client.get(reverse('Hr:employees:list'))
        self.assertEqual(response.status_code, 200)
        
        # Test department list
        response = self.admin_client.get(reverse('Hr:departments:list'))
        self.assertEqual(response.status_code, 200)
        
        # Test job list
        response = self.admin_client.get(reverse('Hr:jobs:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_regular_user_can_access_permitted_pages(self):
        """Test that regular users can access pages they have permission for"""
        # Test employee list (should have access)
        response = self.user_client.get(reverse('Hr:employees:list'))
        self.assertEqual(response.status_code, 200)
        
        # Test department list (should not have access)
        response = self.user_client.get(reverse('Hr:departments:list'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_anonymous_user_redirected_to_login(self):
        """Test that anonymous users are redirected to login page"""
        # Test employee list
        response = self.anonymous_client.get(reverse('Hr:employees:list'))
        self.assertRedirects(
            response, 
            f"{reverse('accounts:login')}?next={reverse('Hr:employees:list')}"
        )
    
    def test_permission_assignment(self):
        """Test that permissions are correctly assigned to groups"""
        # Add more permissions to HR group
        self.hr_group.adminpermission_set.add(self.permissions['departments']['view'])
        
        # Test department list (should now have access)
        response = self.user_client.get(reverse('Hr:departments:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_template_tags(self):
        """Test that template tags correctly check permissions"""
        from Hr.templatetags.hr_permission_tags import has_hr_module_permission
        from django.http import HttpRequest
        
        # Create request objects
        admin_request = HttpRequest()
        admin_request.user = self.admin_user
        
        user_request = HttpRequest()
        user_request.user = self.regular_user
        
        # Admin should have all permissions
        self.assertTrue(has_hr_module_permission(admin_request, 'employees', 'view'))
        self.assertTrue(has_hr_module_permission(admin_request, 'departments', 'add'))
        
        # Regular user should only have employee view permission
        self.assertTrue(has_hr_module_permission(user_request, 'employees', 'view'))
        self.assertFalse(has_hr_module_permission(user_request, 'departments', 'view'))
        self.assertFalse(has_hr_module_permission(user_request, 'employees', 'add'))
