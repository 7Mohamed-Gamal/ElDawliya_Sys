# تطبيق إدارة المخزون (Inventory Application)

## نظرة عامة (Application Overview)

تطبيق إدارة المخزون هو نظام شامل لإدارة مخزن قطع الغيار في شركة الدولية. يوفر إدارة كاملة للأصناف، الموردين، العملاء، الفواتير، وحركات المخزون مع تقارير تفصيلية ونظام تنبيهات للمخزون المنخفض.

**الغرض الرئيسي**: إدارة شاملة لمخزون قطع الغيار مع تتبع دقيق للحركات والكميات.

## الميزات الرئيسية (Key Features)

### 1. إدارة الأصناف (Product Management)
- كتالوج شامل لقطع الغيار
- تصنيفات هرمية للأصناف
- وحدات قياس متعددة
- صور ووصف تفصيلي للأصناف
- تتبع الكميات والمواقع

### 2. إدارة المخزون (Stock Management)
- تتبع الرصيد الحالي والافتتاحي
- حدود دنيا وعليا للأصناف
- تنبيهات المخزون المنخفض
- حركات المخزون التفصيلية
- جرد دوري

### 3. إدارة الموردين والعملاء (Suppliers & Customers)
- قاعدة بيانات شاملة للموردين
- معلومات الاتصال والتعاقد
- تاريخ التعاملات
- تقييم الأداء

### 4. نظام الفواتير والأذونات (Invoices & Vouchers)
- فواتير الشراء والبيع
- أذونات الصرف والإضافة
- ربط تلقائي بحركات المخزون
- طباعة وتصدير الوثائق

### 5. التقارير والتحليلات (Reports & Analytics)
- تقارير المخزون التفصيلية
- تحليل حركات الأصناف
- تقارير الموردين والعملاء
- إحصائيات الأداء

## هيكل النماذج (Models Documentation)

### النماذج المحلية (Local Models)

#### Product (الصنف)
```python
class Product(models.Model):
    product_id = models.CharField(max_length=100, primary_key=True)     # رقم الصنف
    name = models.CharField(max_length=100)                            # اسم الصنف
    category = models.ForeignKey(Category)                             # التصنيف
    unit = models.ForeignKey(Unit)                                     # وحدة القياس
    initial_quantity = models.DecimalField(max_digits=10, decimal_places=2)  # الرصيد الافتتاحي
    quantity = models.DecimalField(max_digits=10, decimal_places=2)     # الرصيد الحالي
    minimum_threshold = models.DecimalField(max_digits=10, decimal_places=2)  # الحد الأدنى
    maximum_threshold = models.DecimalField(max_digits=10, decimal_places=2)  # الحد الأقصى
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)   # سعر الوحدة
    location = models.CharField(max_length=100)                        # الموقع
    description = models.TextField()                                   # الوصف
    image = models.ImageField(upload_to="products/")                   # الصورة
```

#### Category (التصنيف)
```python
class Category(models.Model):
    name = models.CharField(max_length=100)                            # اسم التصنيف
    description = models.TextField()                                   # وصف التصنيف
    parent = models.ForeignKey('self', null=True, blank=True)          # التصنيف الأب
    is_active = models.BooleanField(default=True)                      # نشط
```

#### Supplier (المورد)
```python
class Supplier(models.Model):
    name = models.CharField(max_length=100)                            # اسم المورد
    contact_person = models.CharField(max_length=100)                  # الشخص المسؤول
    phone = models.CharField(max_length=20)                            # الهاتف
    email = models.EmailField()                                        # البريد الإلكتروني
    address = models.TextField()                                       # العنوان
    tax_number = models.CharField(max_length=50)                       # الرقم الضريبي
    payment_terms = models.CharField(max_length=100)                   # شروط الدفع
    is_active = models.BooleanField(default=True)                      # نشط
```

#### Customer (العميل)
```python
class Customer(models.Model):
    name = models.CharField(max_length=100)                            # اسم العميل
    contact_person = models.CharField(max_length=100)                  # الشخص المسؤول
    phone = models.CharField(max_length=20)                            # الهاتف
    email = models.EmailField()                                        # البريد الإلكتروني
    address = models.TextField()                                       # العنوان
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2) # حد الائتمان
    is_active = models.BooleanField(default=True)                      # نشط
```

#### Voucher (الأذن)
```python
class Voucher(models.Model):
    VOUCHER_TYPE_CHOICES = [
        ('in', 'إذن إضافة'),
        ('out', 'إذن صرف'),
        ('transfer', 'إذن نقل'),
        ('adjustment', 'إذن تسوية'),
    ]
    
    voucher_number = models.CharField(max_length=50, unique=True)       # رقم الأذن
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE_CHOICES)  # نوع الأذن
    date = models.DateField()                                          # التاريخ
    supplier = models.ForeignKey(Supplier, null=True, blank=True)      # المورد
    customer = models.ForeignKey(Customer, null=True, blank=True)      # العميل
    department = models.ForeignKey(Department, null=True, blank=True)  # القسم
    notes = models.TextField()                                         # ملاحظات
    total_amount = models.DecimalField(max_digits=10, decimal_places=2) # إجمالي المبلغ
    created_by = models.ForeignKey(User)                               # تم الإنشاء بواسطة
    is_approved = models.BooleanField(default=False)                   # معتمد
```

#### VoucherItem (بند الأذن)
```python
class VoucherItem(models.Model):
    voucher = models.ForeignKey(Voucher, related_name='items')         # الأذن
    product = models.ForeignKey(Product)                               # الصنف
    quantity = models.DecimalField(max_digits=10, decimal_places=2)    # الكمية
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # سعر الوحدة
    total_price = models.DecimalField(max_digits=10, decimal_places=2) # إجمالي السعر
    notes = models.TextField()                                         # ملاحظات
```

### النماذج القديمة (Legacy Models)
النظام يدعم أيضاً النماذج القديمة للتوافق:
- `TblProducts`: جدول الأصناف القديم
- `TblCategories`: جدول التصنيفات القديم
- `TblSuppliers`: جدول الموردين القديم
- `TblCustomers`: جدول العملاء القديم
- `TblInvoices`: جدول الفواتير القديم

## العروض (Views Documentation)

### عروض لوحة التحكم (Dashboard Views)

#### dashboard
```python
def dashboard(request):
    """لوحة تحكم المخزون الرئيسية"""
    # إحصائيات المخزون
    # المنتجات منخفضة المخزون
    # آخر الحركات
    # الرسوم البيانية
```

#### check_low_stock
```python
def check_low_stock(request):
    """فحص المخزون المنخفض"""
    # البحث عن الأصناف تحت الحد الأدنى
    # إرسال تنبيهات
    # إنشاء تقارير
```

### عروض إدارة الأصناف (Product Views)

#### ProductListView
```python
class ProductListView(ListView):
    """عرض قائمة الأصناف مع فلترة متقدمة"""
    model = Product
    template_name = 'inventory/product_list.html'
    
    def get_queryset(self):
        # فلترة حسب البحث
        # فلترة حسب التصنيف
        # فلترة حسب حالة المخزون
```

#### ProductCreateView
```python
class ProductCreateView(CreateView):
    """إنشاء صنف جديد"""
    model = Product
    form_class = ProductForm
    
    def form_valid(self, form):
        # حفظ الصنف
        # تسجيل العملية
        # إرسال تنبيه
```

### عروض الفواتير (Voucher Views)

#### VoucherListView
```python
class VoucherListView(ListView):
    """عرض قائمة الأذونات"""
    model = Voucher
    
    def get_queryset(self):
        # فلترة حسب النوع
        # فلترة حسب التاريخ
        # فلترة حسب الحالة
```

#### create_voucher
```python
def create_voucher(request):
    """إنشاء أذن جديد"""
    # نموذج الأذن
    # إضافة البنود
    # حساب الإجماليات
    # تحديث المخزون
```

## النماذج (Forms Documentation)

### ProductForm
```python
class ProductForm(forms.ModelForm):
    """نموذج إنشاء/تعديل الصنف"""
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'category', 'unit', 'initial_quantity', 
                 'minimum_threshold', 'maximum_threshold', 'unit_price', 'location', 
                 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
```

### VoucherForm
```python
class VoucherForm(forms.ModelForm):
    """نموذج إنشاء الأذن"""
    class Meta:
        model = Voucher
        fields = ['voucher_type', 'date', 'supplier', 'customer', 'department', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'voucher_type': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
```

### CategoryForm
```python
class CategoryForm(forms.ModelForm):
    """نموذج إنشاء التصنيف"""
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }
```

## هيكل URLs (URL Patterns)

### المسارات الرئيسية (Main Routes)
```
/inventory/                         - لوحة التحكم الرئيسية
/inventory/products/                - إدارة الأصناف
/inventory/categories/              - إدارة التصنيفات
/inventory/suppliers/               - إدارة الموردين
/inventory/customers/               - إدارة العملاء
/inventory/vouchers/                - إدارة الأذونات
/inventory/reports/                 - التقارير
/inventory/settings/                - إعدادات النظام
```

### مسارات الأصناف (Product Routes)
```
/inventory/products/                - قائمة الأصناف
/inventory/products/add/            - إضافة صنف جديد
/inventory/products/<id>/edit/      - تعديل صنف
/inventory/products/<id>/delete/    - حذف صنف
/inventory/products/<id>/movements/ - حركات الصنف
```

### مسارات API (API Routes)
```
/inventory/api/search-products/     - البحث عن الأصناف
/inventory/api/product-details/     - تفاصيل الصنف
/inventory/api/stock-levels/        - مستويات المخزون
/inventory/api/low-stock-alert/     - تنبيهات المخزون المنخفض
```

## القوالب (Templates)

### هيكل القوالب (Template Structure)
```
inventory/templates/inventory/
├── base_inventory.html             # القالب الأساسي
├── dashboard.html                  # لوحة التحكم
├── product_list.html               # قائمة الأصناف
├── product_form.html               # نموذج الصنف
├── product_detail.html             # تفاصيل الصنف
├── product_movements.html          # حركات الصنف
├── voucher_list.html               # قائمة الأذونات
├── voucher_form.html               # نموذج الأذن
├── category_list.html              # قائمة التصنيفات
├── supplier_list.html              # قائمة الموردين
├── customer_list.html              # قائمة العملاء
└── reports/                        # قوالب التقارير
    ├── stock_report.html           # تقرير المخزون
    ├── movement_report.html        # تقرير الحركات
    └── supplier_report.html        # تقرير الموردين
```

### ميزات القوالب (Template Features)
- **تصميم متجاوب**: Bootstrap 5 RTL
- **فلترة متقدمة**: بحث وفلترة ديناميكية
- **تصدير البيانات**: Excel, PDF, CSV
- **طباعة**: تقارير قابلة للطباعة
- **AJAX**: تحديثات ديناميكية
- **رسوم بيانية**: Chart.js للإحصائيات

## نظام الصلاحيات (Permission System)

### الوحدات والصلاحيات (Modules & Permissions)
```python
MODULES = {
    "dashboard": "لوحة التحكم",
    "products": "قطع الغيار",
    "categories": "التصنيفات",
    "units": "وحدات القياس",
    "suppliers": "الموردين",
    "customers": "العملاء",
    "vouchers": "الأذونات",
    "reports": "التقارير",
    "settings": "إعدادات النظام",
}
```

### أنواع الصلاحيات (Permission Types)
- `view`: عرض
- `add`: إضافة
- `change`: تعديل
- `delete`: حذف
- `print`: طباعة

### استخدام الصلاحيات (Permission Usage)
```python
@inventory_module_permission_required('products', 'view')
def product_list(request):
    # عرض قائمة الأصناف
    pass

@inventory_module_permission_required('products', 'add')
def product_create(request):
    # إنشاء صنف جديد
    pass
```

## التقارير (Reports)

### تقرير المخزون (Stock Report)
- الرصيد الحالي لجميع الأصناف
- الأصناف تحت الحد الأدنى
- الأصناف المنتهية الصلاحية
- قيمة المخزون الإجمالية

### تقرير الحركات (Movement Report)
- حركات الأصناف خلال فترة محددة
- تفاصيل الإضافة والصرف
- مصادر ووجهات الحركات
- تحليل الاتجاهات

### تقرير الموردين (Supplier Report)
- أداء الموردين
- حجم التعاملات
- تقييم الجودة والسعر
- مواعيد التسليم

## التكامل مع التطبيقات الأخرى (Integration)

### التكامل مع Purchase_orders
```python
# ربط طلبات الشراء بالمخزون
purchase_order = PurchaseOrder.objects.get(id=order_id)
for item in purchase_order.items.all():
    product = Product.objects.get(product_id=item.product_id)
    product.quantity += item.quantity
    product.save()
```

### التكامل مع accounts
```python
# تسجيل العمليات بالمستخدم
voucher = Voucher.objects.create(
    created_by=request.user,
    # باقي البيانات
)
```

## أمثلة الاستخدام (Usage Examples)

### إنشاء صنف جديد
```python
from inventory.models_local import Product, Category, Unit

product = Product.objects.create(
    product_id='P001',
    name='مرشح هواء',
    category=Category.objects.get(name='فلاتر'),
    unit=Unit.objects.get(name='قطعة'),
    initial_quantity=100,
    quantity=100,
    minimum_threshold=10,
    unit_price=25.00
)
```

### إنشاء أذن صرف
```python
from inventory.models_local import Voucher, VoucherItem

voucher = Voucher.objects.create(
    voucher_type='out',
    date=timezone.now().date(),
    department=Department.objects.get(name='الصيانة'),
    created_by=request.user
)

VoucherItem.objects.create(
    voucher=voucher,
    product=Product.objects.get(product_id='P001'),
    quantity=5,
    unit_price=25.00,
    total_price=125.00
)
```

### فحص المخزون المنخفض
```python
from inventory.models_local import Product
from django.db.models import F

low_stock_products = Product.objects.filter(
    quantity__lt=F('minimum_threshold'),
    minimum_threshold__gt=0
)
```

---

**تم إنشاء هذا التوثيق في**: 2025-06-16  
**الإصدار**: 1.0  
**المطور**: فريق تطوير نظام الدولية
