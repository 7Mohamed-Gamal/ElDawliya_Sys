-- Add missing columns to hr_employeetask table

-- Add assigned_by_id column (ForeignKey to User)
ALTER TABLE [hr_employeetask] ADD [assigned_by_id] BIGINT NULL;

-- Add employee_id column (ForeignKey to Employee)
ALTER TABLE [hr_employeetask] ADD [employee_id] INT NOT NULL DEFAULT 1;

-- Change progress column to PositiveInteger
-- SQL Server doesn't have a specific positive integer type, 
-- so we'll need to rely on the application to enforce this
