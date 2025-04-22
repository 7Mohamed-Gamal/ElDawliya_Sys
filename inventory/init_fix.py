# Import models from models_local.py to make them available when importing from the inventory package
from .models_local import (
    Category, Product, Supplier, Customer, 
    Invoice, InvoiceItem, LocalSystemSettings
)