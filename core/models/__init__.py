"""
Core Models Package
===================

This package contains all the core models for the ElDawliya system.
"""

# Base Models
from .base import (
    BaseModel,
    AuditableModel,
    SoftDeleteModel,
    TimestampedModel,
    AddressModel,
    ContactModel,
)

# Audit Models
from .audit import (
    AuditLog,
    SystemLog,
    LoginAttempt,
)

# Permission Models
from .permissions import (
    Module,
    Permission,
    Role,
    UserRole,
    ObjectPermission,
)

# Settings Models
from .settings import (
    SystemSetting,
    UserPreference,
    CompanyProfile,
    NotificationTemplate,
)

# HR Models
from .hr import (
    Department,
    JobPosition,
    Employee,
    EmployeeQualification,
    EmployeeBankAccount,
    EmployeeDocument,
    EmployeeSalary,
    EmployeeInsurance,
)

# Attendance Models
from .attendance import (
    AttendanceRule,
    EmployeeAttendanceProfile,
    AttendanceRecord,
    AttendanceSummary,
)

# Leave Models
from .leaves import (
    LeaveType,
    LeaveBalance,
    LeaveRequest,
    LeaveRecord,
    PublicHoliday,
)

# Payroll Models
from .payroll import (
    PayrollRun,
    PayrollDetail,
    PayrollBonus,
    PayrollDeduction,
)

# Evaluation Models
from .evaluations import (
    EvaluationPeriod,
    EvaluationTemplate,
    EvaluationCriteria,
    EmployeeEvaluation,
    EvaluationCriteriaScore,
    EvaluationGoal,
)

# Inventory Models
from .inventory import (
    ProductCategory,
    Unit,
    Warehouse,
    Supplier,
    Product,
    StockLevel,
    StockMovement,
    StockTake,
    StockTakeItem,
)

# Procurement Models
from .procurement import (
    PurchaseOrder,
    PurchaseOrderLineItem,
    PurchaseRequest,
    PurchaseRequestLineItem,
    GoodsReceipt,
    GoodsReceiptLineItem,
    SupplierQuotation,
    SupplierQuotationLineItem,
)

__all__ = [
    # Base Models
    'BaseModel',
    'AuditableModel',
    'SoftDeleteModel',
    'TimestampedModel',
    'AddressModel',
    'ContactModel',
    
    # Audit Models
    'AuditLog',
    'SystemLog',
    'LoginAttempt',
    
    # Permission Models
    'Module',
    'Permission',
    'Role',
    'UserRole',
    'ObjectPermission',
    
    # Settings Models
    'SystemSetting',
    'UserPreference',
    'CompanyProfile',
    'NotificationTemplate',
    
    # HR Models
    'Department',
    'JobPosition',
    'Employee',
    'EmployeeQualification',
    'EmployeeBankAccount',
    'EmployeeDocument',
    'EmployeeSalary',
    'EmployeeInsurance',
    
    # Attendance Models
    'AttendanceRule',
    'EmployeeAttendanceProfile',
    'AttendanceRecord',
    'AttendanceSummary',
    
    # Leave Models
    'LeaveType',
    'LeaveBalance',
    'LeaveRequest',
    'LeaveRecord',
    'PublicHoliday',
    
    # Payroll Models
    'PayrollRun',
    'PayrollDetail',
    'PayrollBonus',
    'PayrollDeduction',
    
    # Evaluation Models
    'EvaluationPeriod',
    'EvaluationTemplate',
    'EvaluationCriteria',
    'EmployeeEvaluation',
    'EvaluationCriteriaScore',
    'EvaluationGoal',
    
    # Inventory Models
    'ProductCategory',
    'Unit',
    'Warehouse',
    'Supplier',
    'Product',
    'StockLevel',
    'StockMovement',
    'StockTake',
    'StockTakeItem',
    
    # Procurement Models
    'PurchaseOrder',
    'PurchaseOrderLineItem',
    'PurchaseRequest',
    'PurchaseRequestLineItem',
    'GoodsReceipt',
    'GoodsReceiptLineItem',
    'SupplierQuotation',
    'SupplierQuotationLineItem',
]