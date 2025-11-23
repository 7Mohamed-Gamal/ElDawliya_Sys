# نماذج المخزون والمشتريات المحسنة
# Enhanced Inventory and Procurement Models

## نظرة عامة
تم إعادة هيكلة نماذج المخزون والمشتريات لتوفير نظام موحد ومحسن يدعم جميع العمليات المطلوبة مع أفضل الممارسات في تصميم قواعد البيانات.

## الميزات الجديدة

### 1. النماذج الأساسية المحسنة
- **BaseModel**: نموذج أساسي مع UUID، تواريخ الإنشاء والتحديث، والمستخدم المنشئ
- **AuditableModel**: نموذج قابل للمراجعة مع تتبع الإصدارات
- **SoftDeleteModel**: حذف ناعم للبيانات المهمة
- **AddressModel**: نموذج العناوين المشترك
- **ContactModel**: نموذج معلومات الاتصال المشترك

### 2. نماذج المخزون المحسنة

#### تصنيفات المنتجات (ProductCategory)
```python
class ProductCategory(BaseModel):
    name = CharField(max_length=100)           # اسم التصنيف
    code = CharField(max_length=20, unique=True)  # رمز التصنيف
    description = TextField(blank=True)        # الوصف
    parent_category = ForeignKey('self')       # التصنيف الأب (هرمي)
    image = ImageField()                       # صورة التصنيف
    sort_order = PositiveIntegerField()        # ترتيب العرض
```

**الميزات:**
- تصنيفات هرمية (تصنيف رئيسي وفرعي)
- رموز فريدة للتصنيفات
- صور للتصنيفات
- ترتيب مخصص للعرض

#### وحدات القياس (Unit)
```python
class Unit(BaseModel):
    name = CharField(max_length=50, unique=True)     # اسم الوحدة
    symbol = CharField(max_length=10, unique=True)   # رمز الوحدة
    description = TextField(blank=True)              # الوصف
    is_base_unit = BooleanField(default=False)       # وحدة أساسية
    base_unit = ForeignKey('self')                   # الوحدة الأساسية
    conversion_factor = DecimalField()               # معامل التحويل
```

**الميزات:**
- وحدات أساسية وفرعية
- تحويل تلقائي بين الوحدات
- رموز مختصرة للوحدات

#### المخازن (Warehouse)
```python
class Warehouse(BaseModel, AddressModel):
    name = CharField(max_length=100, unique=True)    # اسم المخزن
    code = CharField(max_length=20, unique=True)     # رمز المخزن
    description = TextField(blank=True)              # الوصف
    manager = ForeignKey(User)                       # مدير المخزن
    capacity = DecimalField()                        # السعة الإجمالية
    is_main_warehouse = BooleanField()               # مخزن رئيسي
```

**الميزات:**
- إدارة متعددة المخازن
- تتبع السعة والاستخدام
- مدير مخزن مخصص
- عناوين مفصلة للمخازن

#### الموردين (Supplier)
```python
class Supplier(BaseModel, AddressModel, ContactModel):
    name = CharField(max_length=200)                 # اسم المورد
    code = CharField(max_length=20, unique=True)     # رمز المورد
    supplier_type = CharField(choices=SUPPLIER_TYPES) # نوع المورد
    contact_person = CharField()                     # جهة الاتصال
    tax_number = CharField()                         # الرقم الضريبي
    commercial_registration = CharField()            # السجل التجاري
    payment_terms = CharField(choices=PAYMENT_TERMS) # شروط الدفع
    credit_limit = DecimalField()                    # حد الائتمان
    rating = PositiveIntegerField(1-10)              # التقييم
    is_approved = BooleanField()                     # معتمد
```

**الميزات:**
- تصنيف الموردين (محلي، دولي، مصنع، موزع)
- نظام تقييم الموردين
- إدارة الائتمان وشروط الدفع
- نظام اعتماد الموردين

#### المنتجات (Product)
```python
class Product(AuditableModel):
    name = CharField(max_length=200)                 # اسم المنتج
    code = CharField(max_length=50, unique=True)     # رمز المنتج
    barcode = CharField(unique=True)                 # الباركود
    category = ForeignKey(ProductCategory)           # التصنيف
    product_type = CharField(choices=PRODUCT_TYPES)  # نوع المنتج
    unit = ForeignKey(Unit)                          # وحدة القياس
    description = TextField()                        # الوصف
    specifications = JSONField()                     # المواصفات التقنية
    image = ImageField()                             # صورة المنتج
    
    # التسعير
    cost_price = DecimalField()                      # سعر التكلفة
    selling_price = DecimalField()                   # سعر البيع
    
    # إدارة المخزون
    tracking_method = CharField(choices=TRACKING_METHODS) # طريقة التتبع
    min_stock_level = DecimalField()                 # الحد الأدنى
    max_stock_level = DecimalField()                 # الحد الأقصى
    reorder_point = DecimalField()                   # نقطة إعادة الطلب
    reorder_quantity = DecimalField()                # كمية إعادة الطلب
    
    # مراقبة الجودة
    requires_inspection = BooleanField()             # يتطلب فحص
    shelf_life_days = PositiveIntegerField()         # مدة الصلاحية
    
    # معلومات المورد
    preferred_supplier = ForeignKey(Supplier)        # المورد المفضل
    is_discontinued = BooleanField()                 # متوقف
```

**الميزات:**
- أنواع منتجات متعددة (مادة خام، منتج تام، نصف مصنع، مستهلك، خدمة)
- طرق تتبع متقدمة (رقم تسلسلي، دفعة، تاريخ انتهاء)
- إدارة مستويات المخزون التلقائية
- مواصفات تقنية مرنة (JSON)
- مراقبة الجودة والصلاحية

#### مستويات المخزون (StockLevel)
```python
class StockLevel(BaseModel):
    product = ForeignKey(Product)                    # المنتج
    warehouse = ForeignKey(Warehouse)                # المخزن
    quantity_on_hand = DecimalField()                # الكمية المتاحة
    quantity_reserved = DecimalField()               # الكمية المحجوزة
    quantity_on_order = DecimalField()               # الكمية المطلوبة
    last_movement_date = DateTimeField()             # تاريخ آخر حركة
    average_cost = DecimalField()                    # متوسط التكلفة
```

**الميزات:**
- تتبع المخزون لكل منتج في كل مخزن
- حساب متوسط التكلفة التلقائي
- تتبع الكميات المحجوزة والمطلوبة

#### حركات المخزون (StockMovement)
```python
class StockMovement(AuditableModel):
    movement_number = CharField(unique=True)         # رقم الحركة
    movement_date = DateTimeField()                  # تاريخ الحركة
    movement_type = CharField(choices=MOVEMENT_TYPES) # نوع الحركة
    movement_reason = CharField(choices=MOVEMENT_REASONS) # سبب الحركة
    product = ForeignKey(Product)                    # المنتج
    warehouse = ForeignKey(Warehouse)                # المخزن
    quantity = DecimalField()                        # الكمية
    unit_cost = DecimalField()                       # تكلفة الوحدة
    total_cost = DecimalField()                      # إجمالي التكلفة
    
    # للنقل بين المخازن
    destination_warehouse = ForeignKey(Warehouse)    # المخزن المستقبل
    
    # المراجع
    reference_type = CharField()                     # نوع المرجع
    reference_id = CharField()                       # معرف المرجع
    
    # تتبع الدفعات والأرقام التسلسلية
    batch_number = CharField()                       # رقم الدفعة
    serial_number = CharField()                      # الرقم التسلسلي
    expiry_date = DateField()                        # تاريخ انتهاء الصلاحية
    
    balance_after = DecimalField()                   # الرصيد بعد الحركة
```

**الميزات:**
- أنواع حركات متعددة (استلام، صرف، نقل، تسوية، مرتجع، تالف، فقدان)
- تتبع تلقائي للأرصدة
- ربط بالمستندات المرجعية
- تتبع الدفعات والأرقام التسلسلية

#### جرد المخزون (StockTake)
```python
class StockTake(AuditableModel):
    stock_take_number = CharField(unique=True)       # رقم الجرد
    stock_take_date = DateField()                    # تاريخ الجرد
    warehouse = ForeignKey(Warehouse)                # المخزن
    status = CharField(choices=STATUS_CHOICES)       # الحالة
    conducted_by = ForeignKey(User)                  # أجراه
    approved_by = ForeignKey(User)                   # اعتمده
    approved_at = DateTimeField()                    # تاريخ الاعتماد
    description = TextField()                        # الوصف
```

**الميزات:**
- جرد دوري للمخازن
- سير عمل الموافقة
- تسويات تلقائية للفروقات

### 3. نماذج المشتريات المحسنة

#### طلبات الشراء (PurchaseRequest)
```python
class PurchaseRequest(AuditableModel):
    pr_number = CharField(unique=True)               # رقم طلب الشراء
    pr_date = DateField()                            # تاريخ الطلب
    requested_by = ForeignKey(User)                  # طلب بواسطة
    department = ForeignKey('hr.Department')         # القسم
    status = CharField(choices=STATUS_CHOICES)       # الحالة
    urgency = CharField(choices=URGENCY_CHOICES)     # درجة الإلحاح
    required_date = DateField()                      # التاريخ المطلوب
    justification = TextField()                      # المبرر
    
    # سير عمل الموافقة
    reviewed_by = ForeignKey(User)                   # راجعه
    reviewed_at = DateTimeField()                    # تاريخ المراجعة
    approved_by = ForeignKey(User)                   # اعتمده
    approved_at = DateTimeField()                    # تاريخ الاعتماد
    rejection_reason = TextField()                   # سبب الرفض
    
    # معلومات الميزانية
    estimated_total = DecimalField()                 # إجمالي تقديري
    budget_code = CharField()                        # رمز الميزانية
```

#### أوامر الشراء (PurchaseOrder)
```python
class PurchaseOrder(AuditableModel):
    po_number = CharField(unique=True)               # رقم أمر الشراء
    po_date = DateField()                            # تاريخ أمر الشراء
    supplier = ForeignKey(Supplier)                  # المورد
    warehouse = ForeignKey(Warehouse)                # المخزن المستقبل
    status = CharField(choices=STATUS_CHOICES)       # الحالة
    priority = CharField(choices=PRIORITY_CHOICES)   # الأولوية
    
    # التواريخ
    expected_delivery_date = DateField()             # تاريخ التسليم المتوقع
    actual_delivery_date = DateField()               # تاريخ التسليم الفعلي
    
    # المالية
    subtotal = DecimalField()                        # المجموع الفرعي
    tax_rate = DecimalField()                        # معدل الضريبة
    tax_amount = DecimalField()                      # مبلغ الضريبة
    discount_amount = DecimalField()                 # مبلغ الخصم
    shipping_cost = DecimalField()                   # تكلفة الشحن
    total_amount = DecimalField()                    # المبلغ الإجمالي
    
    # سير عمل الموافقة
    requested_by = ForeignKey(User)                  # طلب بواسطة
    approved_by = ForeignKey(User)                   # اعتمد بواسطة
    approved_at = DateTimeField()                    # تاريخ الاعتماد
    
    # معلومات إضافية
    terms_and_conditions = TextField()               # الشروط والأحكام
    delivery_instructions = TextField()              # تعليمات التسليم
    internal_notes = TextField()                     # ملاحظات داخلية
    
    # مرجع طلب الشراء
    purchase_request = ForeignKey(PurchaseRequest)   # طلب الشراء المرجعي
```

#### إيصالات استلام البضائع (GoodsReceipt)
```python
class GoodsReceipt(AuditableModel):
    grn_number = CharField(unique=True)              # رقم إيصال الاستلام
    grn_date = DateField()                           # تاريخ الاستلام
    purchase_order = ForeignKey(PurchaseOrder)       # أمر الشراء
    warehouse = ForeignKey(Warehouse)                # المخزن
    received_by = ForeignKey(User)                   # استلم بواسطة
    status = CharField(choices=STATUS_CHOICES)       # الحالة
    supplier_invoice_number = CharField()            # رقم فاتورة المورد
    supplier_invoice_date = DateField()              # تاريخ فاتورة المورد
    delivery_note_number = CharField()               # رقم إشعار التسليم
    vehicle_number = CharField()                     # رقم المركبة
    driver_name = CharField()                        # اسم السائق
    quality_check_passed = BooleanField()            # اجتاز فحص الجودة
    quality_notes = TextField()                      # ملاحظات الجودة
    general_notes = TextField()                      # ملاحظات عامة
```

#### عروض أسعار الموردين (SupplierQuotation)
```python
class SupplierQuotation(AuditableModel):
    quotation_number = CharField(unique=True)        # رقم عرض السعر
    quotation_date = DateField()                     # تاريخ العرض
    supplier = ForeignKey(Supplier)                  # المورد
    purchase_request = ForeignKey(PurchaseRequest)   # طلب الشراء
    status = CharField(choices=STATUS_CHOICES)       # الحالة
    valid_until = DateField()                        # صالح حتى
    currency = CharField()                           # العملة
    payment_terms = CharField()                      # شروط الدفع
    delivery_terms = CharField()                     # شروط التسليم
    delivery_time = PositiveIntegerField()           # مدة التسليم
    total_amount = DecimalField()                    # المبلغ الإجمالي
    notes = TextField()                              # ملاحظات
```

## الميزات المتقدمة

### 1. تتبع الدفعات والأرقام التسلسلية
- تتبع المنتجات بالدفعات (Batch Tracking)
- تتبع بالأرقام التسلسلية (Serial Number Tracking)
- تتبع تواريخ انتهاء الصلاحية

### 2. إدارة مستويات المخزون التلقائية
- حساب الحد الأدنى والأقصى للمخزون
- تنبيهات المخزون المنخفض
- نقاط إعادة الطلب التلقائية

### 3. سير عمل الموافقات
- موافقات متعددة المستويات
- تتبع حالة الطلبات والأوامر
- سجل كامل للموافقات والرفض

### 4. تكامل مالي متقدم
- حساب التكاليف التلقائي
- متوسط التكلفة المرجح
- إدارة الضرائب والخصومات

### 5. مراقبة الجودة
- فحص جودة البضائع المستلمة
- تتبع المنتجات المرفوضة
- ملاحظات الجودة المفصلة

## أوامر الإدارة

### ترحيل البيانات من النظام القديم
```bash
python manage.py migrate_inventory_models --dry-run
python manage.py migrate_inventory_models --verbose
```

### التحقق من صحة النماذج
```bash
python scripts/validate_inventory_models.py
python scripts/test_inventory_models_syntax.py
```

## الفهارس المحسنة

تم إضافة فهارس محسنة لتحسين الأداء:

```sql
-- فهارس المنتجات
CREATE INDEX idx_products_code ON products(code);
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_category_active ON products(category_id, is_active);

-- فهارس حركات المخزون
CREATE INDEX idx_stock_movements_date_product ON stock_movements(movement_date, product_id);
CREATE INDEX idx_stock_movements_product_warehouse ON stock_movements(product_id, warehouse_id);
CREATE INDEX idx_stock_movements_type_date ON stock_movements(movement_type, movement_date);

-- فهارس أوامر الشراء
CREATE INDEX idx_purchase_orders_number ON purchase_orders(po_number);
CREATE INDEX idx_purchase_orders_supplier_status ON purchase_orders(supplier_id, status);
CREATE INDEX idx_purchase_orders_date_status ON purchase_orders(po_date, status);
```

## أفضل الممارسات المطبقة

1. **استخدام UUID كمفاتيح أساسية** لضمان الفرادة عبر النظم المختلفة
2. **النماذج الأساسية المشتركة** لتوحيد الحقول المشتركة
3. **التحقق من صحة البيانات** على مستوى النموذج والقاعدة
4. **الفهارس المحسنة** لتحسين أداء الاستعلامات
5. **العلاقات المحسنة** مع استخدام related_name مناسب
6. **التوثيق الشامل** باللغة العربية والإنجليزية
7. **دعم الحذف الناعم** للبيانات المهمة
8. **تتبع المراجعة** لجميع التغييرات المهمة

## الخلاصة

تم إعادة هيكلة نماذج المخزون والمشتريات بشكل شامل لتوفير:
- نظام موحد ومنظم
- أداء محسن
- ميزات متقدمة
- سهولة الصيانة والتطوير
- دعم كامل للمتطلبات التجارية

النماذج الجديدة جاهزة للاستخدام وتدعم جميع العمليات المطلوبة مع إمكانية التوسع المستقبلي.