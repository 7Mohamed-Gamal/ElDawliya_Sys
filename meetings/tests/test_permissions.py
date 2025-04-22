from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from administrator.models import Department, Module, Permission
from meetings.decorators import MODULES, DEPARTMENT_NAME
from meetings.models import Meeting

User = get_user_model()

class MeetingsPermissionsTestCase(TestCase):
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
        
        # Create meetings department
        self.meetings_department = Department.objects.create(
            name=DEPARTMENT_NAME,
            description='قسم إدارة الاجتماعات',
            icon='fas fa-calendar-alt',
            url_name='meetings',
            order=3,
            is_active=True,
        )
        
        # Create meetings modules
        self.modules = {}
        for module_key, module_name in MODULES.items():
            module = Module.objects.create(
                department=self.meetings_department,
                name=module_name,
                description=f'وحدة {module_name}',
                url=f'/meetings/{module_key}/',
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
                    is_active=True,
                )
                module_perms[perm_type] = perm
            self.permissions[module_key] = module_perms
        
        # Create meetings group
        self.meetings_group = Group.objects.create(name='Meetings Staff')
        
        # Add view permissions for meetings to meetings group
        self.meetings_group.adminpermission_set.add(self.permissions['meetings']['view'])
        
        # Add regular user to meetings group
        self.regular_user.groups.add(self.meetings_group)
        
        # Create a test meeting
        self.meeting = Meeting.objects.create(
            title='Test Meeting',
            description='Test Description',
            date='2023-01-01',
            start_time='10:00:00',
            end_time='11:00:00',
            location='Test Location',
            created_by=self.admin_user
        )
        
        # Create clients
        self.admin_client = Client()
        self.admin_client.login(username='admin', password='adminpassword')
        
        self.user_client = Client()
        self.user_client.login(username='user', password='userpassword')
        
        self.anonymous_client = Client()
    
    def test_admin_can_access_all_meetings_pages(self):
        """Test that admin users can access all meetings pages"""
        # Test meeting list
        response = self.admin_client.get(reverse('meetings:list'))
        self.assertEqual(response.status_code, 200)
        
        # Test meeting detail
        response = self.admin_client.get(reverse('meetings:detail', args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Test meeting create
        response = self.admin_client.get(reverse('meetings:create'))
        self.assertEqual(response.status_code, 200)
    
    def test_regular_user_can_access_permitted_pages(self):
        """Test that regular users can access pages they have permission for"""
        # Test meeting list (should have access)
        response = self.user_client.get(reverse('meetings:list'))
        self.assertEqual(response.status_code, 200)
        
        # Test meeting detail (should have access)
        response = self.user_client.get(reverse('meetings:detail', args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Test meeting create (should not have access)
        response = self.user_client.get(reverse('meetings:create'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_anonymous_user_redirected_to_login(self):
        """Test that anonymous users are redirected to login page"""
        # Test meeting list
        response = self.anonymous_client.get(reverse('meetings:list'))
        self.assertRedirects(
            response, 
            f"{reverse('accounts:login')}?next={reverse('meetings:list')}"
        )
    
    def test_permission_assignment(self):
        """Test that permissions are correctly assigned to groups"""
        # Add more permissions to meetings group
        self.meetings_group.adminpermission_set.add(self.permissions['meetings']['add'])
        
        # Test meeting create (should now have access)
        response = self.user_client.get(reverse('meetings:create'))
        self.assertEqual(response.status_code, 200)
    
    def test_template_tags(self):
        """Test that template tags correctly check permissions"""
        from meetings.templatetags.meetings_permission_tags import has_meetings_module_permission
        from django.http import HttpRequest
        
        # Create request objects
        admin_request = HttpRequest()
        admin_request.user = self.admin_user
        
        user_request = HttpRequest()
        user_request.user = self.regular_user
        
        # Admin should have all permissions
        self.assertTrue(has_meetings_module_permission(admin_request, 'meetings', 'view'))
        self.assertTrue(has_meetings_module_permission(admin_request, 'meetings', 'add'))
        
        # Regular user should only have meetings view permission
        self.assertTrue(has_meetings_module_permission(user_request, 'meetings', 'view'))
        self.assertFalse(has_meetings_module_permission(user_request, 'meetings', 'add'))
        self.assertFalse(has_meetings_module_permission(user_request, 'attendees', 'add'))
