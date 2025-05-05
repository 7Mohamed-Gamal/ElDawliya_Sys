from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

# Dummy classes to replace missing Invoice-related models
class Invoice:
    """Placeholder class for the missing Invoice model."""
    pass

class InvoiceItem:
    """Placeholder class for the missing InvoiceItem model."""
    pass

# Dummy view classes to be used in URLs
class InvoiceListView(ListView):
    model = Invoice
    template_name = 'inventory/invoice_list.html'
    context_object_name = 'invoices'

class InvoiceCreateView(CreateView):
    model = Invoice
    template_name = 'inventory/invoice_form.html'
    
class InvoiceUpdateView(UpdateView):
    model = Invoice
    template_name = 'inventory/invoice_form.html'
    
class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = 'inventory/invoice_confirm_delete.html'
    
class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'inventory/invoice_detail.html'
    
class InvoiceItemListView(ListView):
    model = InvoiceItem
    template_name = 'inventory/invoice_item_list.html'
    
class InvoiceItemCreateView(CreateView):
    model = InvoiceItem
    template_name = 'inventory/invoice_item_form.html'
    
class InvoiceItemUpdateView(UpdateView):
    model = InvoiceItem
    template_name = 'inventory/invoice_item_form.html'
    
class InvoiceItemDeleteView(DeleteView):
    model = InvoiceItem
    template_name = 'inventory/invoice_item_confirm_delete.html'
    
class InvoiceItemDetailView(DetailView):
    model = InvoiceItem
    template_name = 'inventory/invoice_item_detail.html'
