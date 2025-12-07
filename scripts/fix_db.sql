-- Fix migration issues for administrator app
-- Insert migration 0003 as applied
INSERT INTO django_migrations (app, name, applied) VALUES ('administrator', '0003_remove_pagepermission_app_module_and_more', datetime('now'));

-- Drop orphaned tables
DROP TABLE IF EXISTS administrator_appmodule;
DROP TABLE IF EXISTS administrator_groupprofile;
DROP TABLE IF EXISTS administrator_operationpermission;
DROP TABLE IF EXISTS administrator_pagepermission;
DROP TABLE IF EXISTS administrator_permission;
DROP TABLE IF EXISTS administrator_permission_groups;
DROP TABLE IF EXISTS administrator_permission_users;
DROP TABLE IF EXISTS administrator_permissionauditlog;
DROP TABLE IF EXISTS administrator_permissiongroup;
DROP TABLE IF EXISTS administrator_permissiongroup_permissions;
DROP TABLE IF EXISTS administrator_templatepermission;
DROP TABLE IF EXISTS administrator_templatepermission_groups;
DROP TABLE IF EXISTS administrator_templatepermission_users;
DROP TABLE IF EXISTS administrator_userdepartmentpermission;
DROP TABLE IF EXISTS administrator_usergroup;
DROP TABLE IF EXISTS administrator_usermodulepermission;
DROP TABLE IF EXISTS administrator_useroperationpermission;
DROP TABLE IF EXISTS administrator_userpagepermission;

-- Verify
SELECT app, name FROM django_migrations WHERE app='administrator' ORDER BY id;

