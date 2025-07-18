"""Organization Services Module

This module provides services for organization management, including:
- Department management
- Branch management
- Job position management
- Company structure management
"""

import uuid
import logging
from datetime import date
from typing import Dict, List, Optional, Tuple, Union, Any

from django.db import transaction
from django.db.models import Q, Count, Sum, Avg, F, Value
from django.utils import timezone

from Hr.models import (
    Company, Branch, Department, JobPosition, Employee
)

# Setup logger
logger = logging.getLogger(__name__)


class CompanyService:
    """Service class for company management operations"""
    
    @staticmethod
    def get_company_by_id(company_id: uuid.UUID) -> Optional[Company]:
        """Retrieve a company by ID
        
        Args:
            company_id: UUID of the company
            
        Returns:
            Company object if found, None otherwise
        """
        try:
            return Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            logger.warning(f"Company with ID {company_id} not found")
            return None
    
    @staticmethod
    def get_all_companies() -> List[Company]:
        """Get all companies
        
        Returns:
            List of Company objects
        """
        return list(Company.objects.all())
    
    @staticmethod
    def get_active_companies() -> List[Company]:
        """Get all active companies
        
        Returns:
            List of active Company objects
        """
        return list(Company.objects.filter(is_active=True))
    
    @staticmethod
    @transaction.atomic
    def create_company(company_data: Dict) -> Tuple[Company, bool, str]:
        """Create a new company
        
        Args:
            company_data: Dictionary with company data
            
        Returns:
            Tuple of (Company object, success boolean, message string)
        """
        try:
            # Check if company with same name already exists
            if Company.objects.filter(name=company_data['name']).exists():
                return None, False, f"Company with name {company_data['name']} already exists"
            
            # Create company
            company = Company(**company_data)
            company.save()
            
            logger.info(f"Created company: {company.name}")
            return company, True, "Company created successfully"
            
        except Exception as e:
            logger.error(f"Error creating company: {str(e)}")
            return None, False, f"Error creating company: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def update_company(company_id: uuid.UUID, company_data: Dict) -> Tuple[Company, bool, str]:
        """Update an existing company
        
        Args:
            company_id: UUID of the company to update
            company_data: Dictionary with updated company data
            
        Returns:
            Tuple of (Company object, success boolean, message string)
        """
        try:
            company = CompanyService.get_company_by_id(company_id)
            if not company:
                return None, False, f"Company with ID {company_id} not found"
            
            # Check if name is being changed and already exists
            if 'name' in company_data and company_data['name'] != company.name:
                if Company.objects.filter(name=company_data['name']).exists():
                    return None, False, f"Company with name {company_data['name']} already exists"
            
            # Update company fields
            for key, value in company_data.items():
                setattr(company, key, value)
            
            company.save()
            
            logger.info(f"Updated company: {company.name}")
            return company, True, "Company updated successfully"
            
        except Exception as e:
            logger.error(f"Error updating company: {str(e)}")
            return None, False, f"Error updating company: {str(e)}"


class BranchService:
    """Service class for branch management operations"""
    
    @staticmethod
    def get_branch_by_id(branch_id: uuid.UUID) -> Optional[Branch]:
        """Retrieve a branch by ID
        
        Args:
            branch_id: UUID of the branch
            
        Returns:
            Branch object if found, None otherwise
        """
        try:
            return Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            logger.warning(f"Branch with ID {branch_id} not found")
            return None
    
    @staticmethod
    def get_all_branches() -> List[Branch]:
        """Get all branches
        
        Returns:
            List of Branch objects
        """
        return list(Branch.objects.all())
    
    @staticmethod
    def get_active_branches() -> List[Branch]:
        """Get all active branches
        
        Returns:
            List of active Branch objects
        """
        return list(Branch.objects.filter(is_active=True))


class DepartmentService:
    """Service class for department management operations"""
    
    @staticmethod
    def get_department_by_id(department_id: uuid.UUID) -> Optional[Department]:
        """Retrieve a department by ID
        
        Args:
            department_id: UUID of the department
            
        Returns:
            Department object if found, None otherwise
        """
        try:
            return Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            logger.warning(f"Department with ID {department_id} not found")
            return None
    
    @staticmethod
    def get_all_departments() -> List[Department]:
        """Get all departments
        
        Returns:
            List of Department objects
        """
        return list(Department.objects.all())
    
    @staticmethod
    def get_active_departments() -> List[Department]:
        """Get all active departments
        
        Returns:
            List of active Department objects
        """
        return list(Department.objects.filter(is_active=True))


class JobPositionService:
    """Service class for job position management operations"""
    
    @staticmethod
    def get_position_by_id(position_id: uuid.UUID) -> Optional[JobPosition]:
        """Retrieve a job position by ID
        
        Args:
            position_id: UUID of the job position
            
        Returns:
            JobPosition object if found, None otherwise
        """
        try:
            return JobPosition.objects.get(id=position_id)
        except JobPosition.DoesNotExist:
            logger.warning(f"Job position with ID {position_id} not found")
            return None
    
    @staticmethod
    def get_all_positions() -> List[JobPosition]:
        """Get all job positions
        
        Returns:
            List of JobPosition objects
        """
        return list(JobPosition.objects.all())
    
    @staticmethod
    def get_active_positions() -> List[JobPosition]:
        """Get all active job positions
        
        Returns:
            List of active JobPosition objects
        """
        return list(JobPosition.objects.filter(is_active=True))