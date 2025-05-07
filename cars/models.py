from django.db import models
# Import the HR app's Employee model
from Hr.models.employee_model import Employee

class Supplier(models.Model):
    """Model for storing supplier information"""
    name = models.CharField(max_length=100, verbose_name="اسم المورد")
    contact_person = models.CharField(max_length=100, verbose_name="الشخص المسؤول", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف", blank=True, null=True)
    email = models.EmailField(verbose_name="البريد الإلكتروني", blank=True, null=True)
    address = models.TextField(verbose_name="العنوان", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "المورد"
        verbose_name_plural = "الموردين"
        ordering = ['name']

# Choices for the Car model
CAR_TYPE_CHOICES = [
    ('microbus', 'ميكروباص'),
    ('bus', 'اتوبيس'),
    ('passenger', 'سيارة 7 راكب'),
    ('private', 'سيارة ملاكي'),
]

FUEL_TYPE_CHOICES = [
    ('diesel', 'جاز'),
    ('gasoline', 'بنزين'),
    ('gas', 'غاز'),
]

CAR_STATUS_CHOICES = [
    ('active', 'نشط'),
    ('inactive', 'غير نشط'),
]

class Car(models.Model):
    """Model for storing car information"""
    car_code = models.CharField(max_length=20, unique=True, verbose_name="كود السيارة")
    car_name = models.CharField(max_length=100, verbose_name="اسم السيارة")
    car_type = models.CharField(max_length=20, choices=CAR_TYPE_CHOICES, verbose_name="نوع السيارة")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars', verbose_name="المورد")
    distance_traveled = models.FloatField(default=0, verbose_name="المسافة المقطوعة")
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, verbose_name="نوع الوقود")
    passengers_count = models.PositiveIntegerField(verbose_name="عدد الركاب")
    car_status = models.CharField(max_length=20, choices=CAR_STATUS_CHOICES, default='active', verbose_name="حالة السيارة")
    fuel_consumption_rate = models.FloatField(help_text="Fuel consumption rate in liters/km", verbose_name="معدل استهلاك الوقود")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.car_code} - {self.car_name}"
    
    class Meta:
        ordering = ['car_code']


class Settings(models.Model):
    """Model for storing system settings and operating costs"""
    diesel_price = models.FloatField(default=10)
    gasoline_price = models.FloatField(default=12)
    gas_price = models.FloatField(default=8)
    maintenance_rate = models.FloatField(default=0.25, help_text="Maintenance cost per km")
    depreciation_rate = models.FloatField(default=0.30, help_text="Depreciation cost per km")
    license_rate = models.FloatField(default=0.10, help_text="License cost per km")
    driver_profit_rate = models.FloatField(default=0.50, help_text="Driver profit per km")
    tax_rate = models.FloatField(default=14, help_text="Tax percentage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings (Last updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    class Meta:
        verbose_name = 'Settings'
        verbose_name_plural = 'Settings'


class Trip(models.Model):
    """Model for storing trip information and calculations"""
    date = models.DateField()
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='trips')
    distance = models.FloatField(help_text="Distance in km")
    
    # These fields will be calculated based on the settings
    fuel_cost = models.FloatField(null=True, blank=True)
    maintenance_cost = models.FloatField(null=True, blank=True)
    depreciation_cost = models.FloatField(null=True, blank=True)
    license_cost = models.FloatField(null=True, blank=True)
    driver_profit = models.FloatField(null=True, blank=True)
    total_base_cost = models.FloatField(null=True, blank=True)
    tax_amount = models.FloatField(null=True, blank=True)
    final_price = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.car.car_name} - {self.date}"
    
    def calculate_costs(self):
        """Calculate all costs based on current settings"""
        settings = Settings.objects.latest('id')
        
        # Determine fuel price based on the car's fuel type
        if self.car.fuel_type == 'diesel':
            fuel_price = settings.diesel_price
        elif self.car.fuel_type == 'gasoline':
            fuel_price = settings.gasoline_price
        else:  # gas
            fuel_price = settings.gas_price
        
        # Calculate all costs
        self.fuel_cost = self.distance * self.car.fuel_consumption_rate * fuel_price
        self.maintenance_cost = self.distance * settings.maintenance_rate
        self.depreciation_cost = self.distance * settings.depreciation_rate
        self.license_cost = self.distance * settings.license_rate
        self.driver_profit = self.distance * settings.driver_profit_rate
        
        # Calculate total base cost and tax
        self.total_base_cost = (self.fuel_cost + self.maintenance_cost + 
                                self.depreciation_cost + self.license_cost + 
                                self.driver_profit)
        self.tax_amount = self.total_base_cost * (settings.tax_rate / 100)
        self.final_price = self.total_base_cost + self.tax_amount
        
        self.save()
        
        # Update the car's total distance traveled
        self.car.distance_traveled += self.distance
        self.car.save()
        
    def save(self, *args, **kwargs):
        is_new = not self.pk  # Check if this is a new record
        super().save(*args, **kwargs)
        
        # Calculate costs if this is a new trip
        if is_new:
            self.calculate_costs()
    
    class Meta:
        ordering = ['-date', 'car__car_code']


# Employee model removed - using HR app's Employee model instead


class RoutePoint(models.Model):
    """Model for storing car route points"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='route_points', verbose_name="السيارة")
    point_name = models.CharField(max_length=100, verbose_name="اسم النقطة")
    departure_time = models.TimeField(verbose_name="وقت المغادرة")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    employees = models.ManyToManyField('Hr.Employee', related_name='car_route_points', blank=True, verbose_name="الموظفين")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.car.car_name} - {self.point_name}"
    
    class Meta:
        verbose_name = "نقطة خط السير"
        verbose_name_plural = "نقاط خط السير"
        ordering = ['car', 'order']
        unique_together = ['car', 'order']
