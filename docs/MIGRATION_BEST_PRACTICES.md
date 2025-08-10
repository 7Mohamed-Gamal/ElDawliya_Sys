# Django Migration Best Practices & Conflict Resolution

## Overview
This document outlines best practices for managing Django migrations and resolving conflicts in the HRMS system.

## Recent Resolution: Hr App Migration 0009

### Problem
- Migration `0009_attendancerule_hrattendancemachine_hrattendancerule_and_more.py` failed with:
  ```
  django.db.utils.ProgrammingError: There is already an object named 'Hr_AttendanceMachine' in the database.
  ```

### Root Cause
- Tables already existed in the database from previous operations
- Django's migration system didn't recognize the existing tables
- Migration tried to create tables that already existed

### Solution Applied
```bash
# Fake the migration to mark it as applied without running SQL
python manage.py migrate Hr 0009 --fake
```

### Verification
- ✅ Migration marked as applied: `python manage.py showmigrations Hr`
- ✅ No pending migrations: `python manage.py migrate`
- ✅ System check passes: `python manage.py check`
- ✅ Models accessible: All Hr models import correctly
- ✅ URL namespace works: `reverse('Hr:dashboard')` resolves

## Best Practices for Future Migrations

### 1. Pre-Migration Checks
```bash
# Always check migration status before applying
python manage.py showmigrations

# Check for any issues
python manage.py check

# Dry run to see what would be created
python manage.py makemigrations --dry-run
```

### 2. Safe Migration Process
```bash
# Step 1: Create migrations
python manage.py makemigrations

# Step 2: Review the migration file
# Check for potential conflicts with existing tables

# Step 3: Test on development database first
python manage.py migrate --verbosity=2

# Step 4: If conflicts occur, use appropriate resolution strategy
```

### 3. Conflict Resolution Strategies

#### Strategy 1: Fake Migration (Recommended for existing tables)
```bash
# When tables already exist and match the migration
python manage.py migrate <app> <migration_number> --fake
```

#### Strategy 2: Fake Initial (For new apps with existing data)
```bash
# When setting up Django on existing database
python manage.py migrate <app> --fake-initial
```

#### Strategy 3: Manual Table Rename (When structure differs)
```sql
-- Rename existing table if structure doesn't match
EXEC sp_rename 'old_table_name', 'backup_old_table_name'
-- Then run migration normally
```

#### Strategy 4: Drop and Recreate (Data loss - use with caution)
```sql
-- Only if data can be safely lost
DROP TABLE existing_table_name;
-- Then run migration normally
```

### 4. Prevention Strategies

#### Model Naming Conventions
- Use unique prefixes for models (e.g., `Hr` prefix for Hr app models)
- Avoid generic names that might conflict across apps
- Use explicit `db_table` names to control table naming

#### Migration Management
- Keep migrations small and focused
- Test migrations on development environment first
- Use version control to track migration files
- Document any manual database changes

#### Database Schema Management
- Maintain schema documentation
- Use database migration tools consistently
- Avoid manual schema changes when possible
- Backup database before major migrations

### 5. Troubleshooting Common Issues

#### Issue: "Table already exists"
```bash
# Solution: Fake the migration
python manage.py migrate <app> <migration> --fake
```

#### Issue: "Column already exists"
```bash
# Solution: Create custom migration to handle existing column
python manage.py makemigrations --empty <app>
# Edit migration to check if column exists before adding
```

#### Issue: "Foreign key constraint fails"
```bash
# Solution: Ensure referenced tables exist first
# Check migration dependencies
# May need to adjust migration order
```

### 6. Monitoring and Maintenance

#### Regular Checks
```bash
# Weekly migration status check
python migration_conflict_resolver.py status

# Check for unapplied migrations
python manage.py showmigrations | grep "\[ \]"

# Verify database consistency
python manage.py check --database default
```

#### Documentation
- Document any manual database changes
- Keep track of faked migrations and reasons
- Maintain changelog of schema modifications

## Emergency Procedures

### If Migration Fails Mid-Process
1. **Don't Panic** - Django migrations are transactional
2. **Check Error Message** - Identify the specific issue
3. **Rollback if Needed** - Use `--fake` to mark as unapplied
4. **Fix the Issue** - Address the root cause
5. **Retry Migration** - Apply the corrected migration

### Database Recovery
```bash
# If migration corrupts data
# 1. Restore from backup
# 2. Apply migrations one by one with --verbosity=2
# 3. Use --fake for problematic migrations
# 4. Verify data integrity
```

## Tools and Scripts

### migration_conflict_resolver.py
```bash
# Check for conflicts
python migration_conflict_resolver.py check

# Resolve Hr app conflicts
python migration_conflict_resolver.py resolve

# Show migration status
python migration_conflict_resolver.py status
```

## Contact and Support

For migration issues:
1. Check this documentation first
2. Use the migration_conflict_resolver.py script
3. Test solutions on development environment
4. Document any new patterns or solutions

## Changelog

- **2025-07-09**: Resolved Hr app migration 0009 conflict using fake migration strategy
- **2025-07-09**: Created migration conflict resolver script
- **2025-07-09**: Established best practices documentation
