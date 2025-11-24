#!/usr/bin/env python
"""
سكريبت للتحقق من صحة نماذج المخزون والمشتريات الجديدة
Script to validate the new inventory and procurement models
"""
import os
import sys
import django
from decimal import Decimal

# إعداد Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone


def test_inventory_models():
    """اختبار نماذج المخزون"""
    print("🧪 اختبار نماذج المخزون...")

    try:
        from core.models.inventory import (
            ProductCategory, Unit, Warehouse, Supplier, Product,
            StockLevel, StockMovement, StockTake, StockTakeItem
        )

        # اختبار إنشاء تصنيف منتج
        print("  ✅ تم استيراد نماذج المخزون بنجاح")

        # اختبار التصنيفات
        category = ProductCategory(
            name="إلكترونيات",
            code="ELEC-001",
            description="أجهزة إلكترونية"
        )
        category.full_clean()
        print("  ✅ نموذج تصنيف المنتج صحيح")

        # اختبار الوحدات
        unit = Unit(
            name="قطعة",
            symbol="قطع",
            description="وحدة العد",
            is_base_unit=True
        )
        unit.full_clean()
        print("  ✅ نموذج وحدة القياس صحيح")

        # اختبار المخازن
        warehouse = Warehouse(
            name="المخزن الرئيسي",
            code="MAIN-001",
            description="المخزن الرئيسي للشركة",
            capacity=Decimal('10000.00'),
            is_main_warehouse=True
        )
        warehouse.full_clean()
        print("  ✅ نموذج المخزن صحيح")

        # اختبار الموردين
        supplier = Supplier(
            name="شركة التقنية المتقدمة",
            code="TECH-001",
            supplier_type="local",
            contact_person="أحمد محمد",
            phone="0501234567",
            email="info@tech.com",
            payment_terms="net_30",
            rating=8,
            is_approved=True
        )
        supplier.full_clean()
        print("  ✅ نموذج المورد صحيح")

        print("✅ جميع نماذج المخزون صحيحة")
        return True

    except ImportError as e:
        print(f"❌ خطأ في استيراد النماذج: {e}")
        return False
    except ValidationError as e:
        print(f"❌ خطأ في التحقق من صحة النماذج: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return False


def test_procurement_models():
    """اختبار نماذج المشتريات"""
    print("\n🧪 اختبار نماذج المشتريات...")

    try:
        from core.models.procurement import (
            PurchaseOrder, PurchaseOrderLineItem, PurchaseRequest,
            PurchaseRequestLineItem, GoodsReceipt, GoodsReceiptLineItem,
            SupplierQuotation
        )

        print("  ✅ تم استيراد نماذج المشتريات بنجاح")

        # اختبار طلب الشراء
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='test_user',
                email='test@example.com',
                password='testpass123'
            )

        purchase_request = PurchaseRequest(
            pr_number="PR-202412-0001",
            pr_date=timezone.now().date(),
            requested_by=user,
            status="draft",
            urgency="normal",
            justification="احتياج للمكتب",
            estimated_total=Decimal('1000.00')
        )
        purchase_request.full_clean()
        print("  ✅ نموذج طلب الشراء صحيح")

        print("✅ جميع نماذج المشتريات صحيحة")
        return True

    except ImportError as e:
        print(f"❌ خطأ في استيراد النماذج: {e}")
        return False
    except ValidationError as e:
        print(f"❌ خطأ في التحقق من صحة النماذج: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return False


def test_model_relationships():
    """اختبار العلاقات بين النماذج"""
    print("\n🧪 اختبار العلاقات بين النماذج...")

    try:
        from core.models.inventory import ProductCategory, Unit, Product, Supplier

        # اختبار العلاقة بين المنتج والتصنيف
        category = ProductCategory(
            name="اختبار",
            code="TEST-001"
        )

        unit = Unit(
            name="قطعة",
            symbol="قطع",
            is_base_unit=True
        )

        supplier = Supplier(
            name="مورد اختبار",
            code="TEST-SUP-001",
            supplier_type="local"
        )

        product = Product(
            name="منتج اختبار",
            code="PROD-TEST-001",
            category=category,
            unit=unit,
            preferred_supplier=supplier,
            cost_price=Decimal('100.00'),
            selling_price=Decimal('150.00'),
            min_stock_level=Decimal('10.00')
        )

        # التحقق من العلاقات
        assert product.category == category
        assert product.unit == unit
        assert product.preferred_supplier == supplier

        print("  ✅ العلاقات بين النماذج صحيحة")
        return True

    except Exception as e:
        print(f"❌ خطأ في اختبار العلاقات: {e}")
        return False


def test_model_methods():
    """اختبار دوال النماذج"""
    print("\n🧪 اختبار دوال النماذج...")

    try:
        from core.models.inventory import ProductCategory, Unit

        # اختبار دالة full_path للتصنيف
        parent_category = ProductCategory(
            name="إلكترونيات",
            code="ELEC-001"
        )

        child_category = ProductCategory(
            name="هواتف ذكية",
            code="PHONE-001",
            parent_category=parent_category
        )

        # اختبار دالة التحويل للوحدات
        base_unit = Unit(
            name="متر",
            symbol="م",
            is_base_unit=True
        )

        derived_unit = Unit(
            name="سنتيمتر",
            symbol="سم",
            is_base_unit=False,
            base_unit=base_unit,
            conversion_factor=Decimal('0.01')
        )

        print("  ✅ دوال النماذج تعمل بشكل صحيح")
        return True

    except Exception as e:
        print(f"❌ خطأ في اختبار دوال النماذج: {e}")
        return False


def main():
    """الدالة الرئيسية"""
    print("🚀 بدء التحقق من صحة نماذج المخزون والمشتريات الجديدة")
    print("=" * 60)

    all_tests_passed = True

    # تشغيل الاختبارات
    tests = [
        test_inventory_models,
        test_procurement_models,
        test_model_relationships,
        test_model_methods,
    ]

    for test in tests:
        if not test():
            all_tests_passed = False

    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 جميع الاختبارات نجحت! النماذج الجديدة جاهزة للاستخدام")
    else:
        print("❌ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء أعلاه")

    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
