"""
Product movement views for the inventory application.
"""
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import F, Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from inventory.decorators import inventory_class_permission_required
from inventory.models_local import Product, VoucherItem

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'view')
class ProductMovementView(ListView):
    """عرض حركات الصنف"""
    model = VoucherItem
    template_name = 'inventory/product_movements.html'
    context_object_name = 'movements'

    def get_queryset(self):
        """
        Get all voucher items related to the specified product.
        """
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, product_id=product_id)
        
        queryset = VoucherItem.objects.filter(
            product=product
        ).select_related('voucher', 'product').order_by('-voucher__date')
        
        return queryset

    def get_context_data(self, **kwargs):
        """
        Add product information to the context.
        """
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, product_id=product_id)
        
        # Calculate movement totals
        movements = self.get_queryset()
        total_additions = 0
        total_disbursements = 0
        total_customer_returns = 0
        total_supplier_returns = 0
        
        for item in movements:
            # Addition vouchers
            if item.voucher.voucher_type == 'إذن اضافة' and item.quantity_added:
                total_additions += float(item.quantity_added)
            # Disbursement vouchers
            elif item.voucher.voucher_type == 'إذن صرف' and item.quantity_disbursed:
                total_disbursements += float(item.quantity_disbursed)
            # Customer return vouchers
            elif item.voucher.voucher_type == 'اذن مرتجع عميل' and item.quantity_added:
                total_customer_returns += float(item.quantity_added)
            # Supplier return vouchers
            elif item.voucher.voucher_type == 'إذن مرتجع مورد' and item.quantity_disbursed:
                total_supplier_returns += float(item.quantity_disbursed)
        
        context['product'] = product
        context['page_title'] = f'حركات الصنف: {product.name}'
        context['total_additions'] = total_additions
        context['total_disbursements'] = total_disbursements
        context['total_customer_returns'] = total_customer_returns
        context['total_supplier_returns'] = total_supplier_returns
        
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        
        return context

@method_decorator(login_required, name='dispatch')
@inventory_class_permission_required('products', 'view')
class ProductMovementListView(ListView):
    """عرض قائمة الأصناف للوصول إلى حركات الصنف"""
    model = Product
    template_name = 'inventory/product_movement_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')

        if search_query:
            queryset = queryset.filter(
                Q(product_id__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(location__icontains=search_query)
            )

        if category:
            queryset = queryset.filter(category__id=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'قائمة الأصناف - حركات الصنف'
        
        # Add low stock count for sidebar
        low_stock_count = Product.objects.filter(
            quantity__lt=F('minimum_threshold'),
            minimum_threshold__gt=0
        ).count()
        context['low_stock_count'] = low_stock_count
        
        return context
