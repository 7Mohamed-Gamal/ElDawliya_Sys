"""
Inventory API Serializers
مسلسلات API المخزون
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.Serializer):
    """
    Serializer for Category model
    مسلسل نموذج الفئة
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    name_ar = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    parent_name = serializers.CharField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    product_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)


class SupplierSerializer(serializers.Serializer):
    """
    Serializer for Supplier model
    مسلسل نموذج المورد
    """
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=200)
    name_ar = serializers.CharField(max_length=200, required=False)
    supplier_code = serializers.CharField(max_length=20, required=False)
    
    # Contact Information
    contact_person = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    mobile = serializers.CharField(max_length=20, required=False)
    fax = serializers.CharField(max_length=20, required=False)
    website = serializers.URLField(required=False)
    
    # Address Information
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False)
    state = serializers.CharField(max_length=100, required=False)
    country = serializers.CharField(max_length=100, required=False)
    postal_code = serializers.CharField(max_length=10, required=False)
    
    # Business Information
    tax_number = serializers.CharField(max_length=50, required=False)
    commercial_register = serializers.CharField(max_length=50, required=False)
    supplier_type = serializers.ChoiceField(
        choices=[
            ('local', 'محلي'),
            ('international', 'دولي'),
            ('manufacturer', 'مصنع'),
            ('distributor', 'موزع'),
            ('wholesaler', 'تاجر جملة'),
            ('retailer', 'تاجر تجزئة')
        ],
        required=False
    )
    
    # Financial Information
    credit_limit = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    payment_terms = serializers.CharField(max_length=100, required=False)
    currency = serializers.CharField(max_length=3, default='SAR')
    
    # Performance Metrics
    rating = serializers.FloatField(min_value=1, max_value=5, required=False)
    total_orders = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    on_time_delivery_rate = serializers.FloatField(read_only=True)
    quality_rating = serializers.FloatField(read_only=True)
    
    # Status
    is_active = serializers.BooleanField(default=True)
    is_approved = serializers.BooleanField(default=False)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class WarehouseSerializer(serializers.Serializer):
    """
    Serializer for Warehouse model
    مسلسل نموذج المخزن
    """
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=200)
    name_ar = serializers.CharField(max_length=200, required=False)
    code = serializers.CharField(max_length=20, required=False)
    
    # Location Information
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False)
    country = serializers.CharField(max_length=100, required=False)
    postal_code = serializers.CharField(max_length=10, required=False)
    
    # Warehouse Details
    warehouse_type = serializers.ChoiceField(
        choices=[
            ('main', 'مخزن رئيسي'),
            ('branch', 'مخزن فرع'),
            ('transit', 'مخزن عبور'),
            ('quarantine', 'مخزن حجر'),
            ('damaged', 'مخزن تالف'),
            ('virtual', 'مخزن افتراضي')
        ],
        default='main'
    )
    
    # Capacity Information
    total_capacity = serializers.FloatField(required=False)
    used_capacity = serializers.FloatField(read_only=True)
    available_capacity = serializers.FloatField(read_only=True)
    capacity_unit = serializers.CharField(max_length=20, default='m3')
    
    # Manager Information
    manager_id = serializers.UUIDField(required=False, allow_null=True)
    manager_name = serializers.CharField(read_only=True)
    
    # Status and Settings
    is_active = serializers.BooleanField(default=True)
    allow_negative_stock = serializers.BooleanField(default=False)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ProductSerializer(serializers.Serializer):
    """
    Serializer for Product model
    مسلسل نموذج المنتج
    """
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=200)
    name_ar = serializers.CharField(max_length=200, required=False)
    sku = serializers.CharField(max_length=50, required=False)
    barcode = serializers.CharField(max_length=50, required=False)
    
    # Category and Classification
    category_id = serializers.IntegerField()
    category = CategorySerializer(read_only=True)
    subcategory = serializers.CharField(max_length=100, required=False)
    brand = serializers.CharField(max_length=100, required=False)
    model = serializers.CharField(max_length=100, required=False)
    
    # Description and Specifications
    description = serializers.CharField(required=False, allow_blank=True)
    specifications = serializers.JSONField(required=False)
    
    # Units and Measurements
    unit_of_measure = serializers.CharField(max_length=20, default='piece')
    weight = serializers.FloatField(required=False)
    weight_unit = serializers.CharField(max_length=10, default='kg')
    dimensions = serializers.JSONField(required=False)  # {length, width, height}
    
    # Pricing Information
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    selling_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(max_length=3, default='SAR')
    
    # Stock Information
    quantity_in_stock = serializers.FloatField(read_only=True)
    available_quantity = serializers.FloatField(read_only=True)
    reserved_quantity = serializers.FloatField(read_only=True)
    
    # Stock Levels
    minimum_stock_level = serializers.FloatField(required=False, default=0)
    maximum_stock_level = serializers.FloatField(required=False)
    reorder_point = serializers.FloatField(required=False)
    reorder_quantity = serializers.FloatField(required=False)
    
    # Supplier Information
    primary_supplier_id = serializers.UUIDField(required=False, allow_null=True)
    primary_supplier = SupplierSerializer(read_only=True)
    supplier_part_number = serializers.CharField(max_length=50, required=False)
    
    # Product Status
    product_type = serializers.ChoiceField(
        choices=[
            ('finished_good', 'منتج نهائي'),
            ('raw_material', 'مادة خام'),
            ('component', 'مكون'),
            ('service', 'خدمة'),
            ('kit', 'طقم'),
            ('virtual', 'افتراضي')
        ],
        default='finished_good'
    )
    
    is_active = serializers.BooleanField(default=True)
    is_serialized = serializers.BooleanField(default=False)
    is_perishable = serializers.BooleanField(default=False)
    shelf_life_days = serializers.IntegerField(required=False)
    
    # Tracking Information
    lot_tracking = serializers.BooleanField(default=False)
    serial_tracking = serializers.BooleanField(default=False)
    expiry_tracking = serializers.BooleanField(default=False)
    
    # Images and Attachments
    image_url = serializers.URLField(required=False)
    images = serializers.JSONField(required=False)  # Array of image URLs
    attachments = serializers.JSONField(required=False)  # Array of file URLs
    
    # Computed Fields
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    turnover_rate = serializers.FloatField(read_only=True)
    days_in_stock = serializers.IntegerField(read_only=True)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class InventoryMovementSerializer(serializers.Serializer):
    """
    Serializer for Inventory Movement model
    مسلسل نموذج حركة المخزون
    """
    id = serializers.UUIDField(read_only=True)
    
    # Product and Warehouse
    product_id = serializers.UUIDField()
    product = ProductSerializer(read_only=True)
    warehouse_id = serializers.UUIDField()
    warehouse = WarehouseSerializer(read_only=True)
    
    # Movement Details
    movement_type = serializers.ChoiceField(
        choices=[
            ('receipt', 'استلام'),
            ('issue', 'إصدار'),
            ('transfer_in', 'تحويل داخل'),
            ('transfer_out', 'تحويل خارج'),
            ('adjustment', 'تعديل'),
            ('return', 'إرجاع'),
            ('damage', 'تلف'),
            ('loss', 'فقدان'),
            ('found', 'عثور'),
            ('production', 'إنتاج'),
            ('consumption', 'استهلاك')
        ]
    )
    
    # Quantities
    quantity = serializers.FloatField()
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    total_cost = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    # Balance Information
    balance_before = serializers.FloatField(read_only=True)
    balance_after = serializers.FloatField(read_only=True)
    
    # Reference Information
    reference_type = serializers.ChoiceField(
        choices=[
            ('purchase_order', 'أمر شراء'),
            ('sales_order', 'أمر بيع'),
            ('transfer_order', 'أمر تحويل'),
            ('adjustment', 'تعديل'),
            ('production_order', 'أمر إنتاج'),
            ('manual', 'يدوي'),
            ('system', 'نظام')
        ],
        required=False
    )
    reference_number = serializers.CharField(max_length=50, required=False)
    reference_id = serializers.UUIDField(required=False, allow_null=True)
    
    # Lot and Serial Tracking
    lot_number = serializers.CharField(max_length=50, required=False)
    serial_number = serializers.CharField(max_length=50, required=False)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    
    # Additional Information
    notes = serializers.CharField(required=False, allow_blank=True)
    created_by_id = serializers.UUIDField(read_only=True)
    created_by_name = serializers.CharField(read_only=True)
    
    created_at = serializers.DateTimeField(read_only=True)


class InventoryAdjustmentSerializer(serializers.Serializer):
    """
    Serializer for Inventory Adjustment model
    مسلسل نموذج تعديل المخزون
    """
    id = serializers.UUIDField(read_only=True)
    
    # Product and Warehouse
    product_id = serializers.UUIDField()
    product = ProductSerializer(read_only=True)
    warehouse_id = serializers.UUIDField()
    warehouse = WarehouseSerializer(read_only=True)
    
    # Adjustment Details
    adjustment_type = serializers.ChoiceField(
        choices=[
            ('physical_count', 'جرد فعلي'),
            ('damage', 'تلف'),
            ('loss', 'فقدان'),
            ('found', 'عثور'),
            ('expiry', 'انتهاء صلاحية'),
            ('quality_issue', 'مشكلة جودة'),
            ('system_error', 'خطأ نظام'),
            ('other', 'أخرى')
        ]
    )
    
    # Quantities
    system_quantity = serializers.FloatField(read_only=True)
    actual_quantity = serializers.FloatField()
    quantity_adjusted = serializers.FloatField(read_only=True)
    
    # Cost Information
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    total_cost_impact = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    # Reason and Documentation
    reason = serializers.CharField(required=False, allow_blank=True)
    supporting_documents = serializers.JSONField(required=False)
    
    # Approval Workflow
    status = serializers.ChoiceField(
        choices=[
            ('draft', 'مسودة'),
            ('pending_approval', 'في انتظار الموافقة'),
            ('approved', 'موافق عليه'),
            ('rejected', 'مرفوض'),
            ('applied', 'مطبق')
        ],
        default='draft'
    )
    
    # Approval Information
    approved_by_id = serializers.UUIDField(required=False, allow_null=True)
    approved_by_name = serializers.CharField(read_only=True)
    approved_at = serializers.DateTimeField(read_only=True)
    approval_comments = serializers.CharField(required=False, allow_blank=True)
    
    # Audit Information
    created_by_id = serializers.UUIDField(read_only=True)
    created_by_name = serializers.CharField(read_only=True)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


# Additional serializers for specific operations

class BulkProductImportSerializer(serializers.Serializer):
    """
    Serializer for bulk product import
    مسلسل الاستيراد المجمع للمنتجات
    """
    file = serializers.FileField()
    format = serializers.ChoiceField(choices=['excel', 'csv'], default='excel')
    skip_duplicates = serializers.BooleanField(default=True)
    update_existing = serializers.BooleanField(default=False)
    default_warehouse_id = serializers.UUIDField(required=False)


class InventoryReceiptSerializer(serializers.Serializer):
    """
    Serializer for inventory receipt
    مسلسل استلام المخزون
    """
    warehouse_id = serializers.UUIDField()
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    reference_number = serializers.CharField(max_length=50, required=False)
    receipt_date = serializers.DateField()
    
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    notes = serializers.CharField(required=False, allow_blank=True)


class InventoryIssueSerializer(serializers.Serializer):
    """
    Serializer for inventory issue
    مسلسل إصدار المخزون
    """
    warehouse_id = serializers.UUIDField()
    issue_to = serializers.CharField(max_length=200)
    reference_number = serializers.CharField(max_length=50, required=False)
    issue_date = serializers.DateField()
    
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    notes = serializers.CharField(required=False, allow_blank=True)


class InventoryTransferSerializer(serializers.Serializer):
    """
    Serializer for inventory transfer
    مسلسل نقل المخزون
    """
    from_warehouse_id = serializers.UUIDField()
    to_warehouse_id = serializers.UUIDField()
    reference_number = serializers.CharField(max_length=50, required=False)
    transfer_date = serializers.DateField()
    
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    notes = serializers.CharField(required=False, allow_blank=True)


class StockLevelSerializer(serializers.Serializer):
    """
    Serializer for stock level information
    مسلسل معلومات مستوى المخزون
    """
    product_id = serializers.UUIDField()
    product_name = serializers.CharField()
    warehouse_id = serializers.UUIDField()
    warehouse_name = serializers.CharField()
    
    quantity_in_stock = serializers.FloatField()
    available_quantity = serializers.FloatField()
    reserved_quantity = serializers.FloatField()
    
    minimum_stock_level = serializers.FloatField()
    maximum_stock_level = serializers.FloatField()
    reorder_point = serializers.FloatField()
    
    stock_status = serializers.CharField()  # normal, low, critical, overstock
    days_of_supply = serializers.IntegerField()
    
    last_movement_date = serializers.DateTimeField()
    last_receipt_date = serializers.DateTimeField()


class SupplierEvaluationSerializer(serializers.Serializer):
    """
    Serializer for supplier evaluation
    مسلسل تقييم المورد
    """
    supplier_id = serializers.UUIDField()
    evaluation_period = serializers.CharField(max_length=7)  # YYYY-MM
    
    # Evaluation Criteria (1-5 scale)
    quality_rating = serializers.IntegerField(min_value=1, max_value=5)
    delivery_rating = serializers.IntegerField(min_value=1, max_value=5)
    price_rating = serializers.IntegerField(min_value=1, max_value=5)
    service_rating = serializers.IntegerField(min_value=1, max_value=5)
    communication_rating = serializers.IntegerField(min_value=1, max_value=5)
    
    # Overall Rating
    overall_rating = serializers.FloatField(read_only=True)
    
    # Comments
    strengths = serializers.CharField(required=False, allow_blank=True)
    areas_for_improvement = serializers.CharField(required=False, allow_blank=True)
    recommendations = serializers.CharField(required=False, allow_blank=True)
    
    # Evaluator Information
    evaluated_by_id = serializers.UUIDField(read_only=True)
    evaluated_by_name = serializers.CharField(read_only=True)
    
    created_at = serializers.DateTimeField(read_only=True)