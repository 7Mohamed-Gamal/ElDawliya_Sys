import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from accounts.models import Users_Login_New

# Find admin user
user = Users_Login_New.objects.filter(username__iexact='admin').first()

if user:
    print(f"✅ User found: {user.username}")
    print(f"   IsActive: {user.IsActive}")
    print(f"   Password hash: {user.password[:60]}...")
    
    # Test password
    test_password = "hgslduhgfwdv"
    is_correct = user.check_password(test_password)
    print(f"   Password '{test_password}' is correct: {is_correct}")
    
    if not is_correct:
        print("\n⚠️  Password is incorrect! Setting new password...")
        user.set_password(test_password)
        user.save()
        print(f"✅ Password updated successfully!")
        print(f"   New password hash: {user.password[:60]}...")
else:
    print("❌ No admin user found!")
    print("\nCreating admin user...")
    user = Users_Login_New.objects.create_user(
        username='admin',
        password='hgslduhgfwdv',
        IsActive=True
    )
    print(f"✅ Admin user created: {user.username}")

