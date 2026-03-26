from django.db import models
from django.contrib.auth.models import User

# -----------------------------------------------------------------------------
# 0. AUTHENTICATION & USERS
# -----------------------------------------------------------------------------

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile_number = models.CharField(max_length=20, blank=True, null=True, help_text="Used for Owner OTP login")

    def __str__(self):
        return f"{self.user.username}'s Profile"
# -----------------------------------------------------------------------------
# 1. STUDY SECTION MODELS
# These models act as the "Master Lists" for autocomplete suggestions.
# -----------------------------------------------------------------------------

class Mechanic(models.Model):
    """
    Represents a mechanic working in the shop.
    Used for tracking who performed jobs without requiring individual logins.
    """
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True, help_text="Disable if the mechanic leaves the company")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CarBrand(models.Model):
    """
    Represents a Car Brand (e.g., Toyota, BMW).
    Used for the Study section grid and autocomplete source.
    """
    name = models.CharField(max_length=100, unique=True)
    logo_image = models.ImageField(upload_to='brands/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CarModel(models.Model):
    """
    Represents a Car Model (e.g., Corolla, 3 Series) linked to a Brand.
    Used for the Study section grid and autocomplete source.
    """
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('brand', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class SparePart(models.Model):
    """
    Represents a common Spare Part name (e.g., Oil Filter, Brake Pad).
    Used as the master list for autocomplete suggestions.
    """
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ConcernSolution(models.Model):
    """
    Knowledge base for common Concerns.
    """
    concern = models.TextField(help_text="e.g., Sound when applying brake")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.concern[:50]}..."


# -----------------------------------------------------------------------------
# 2. JOB CARD SECTION MODELS
# These handle the daily work. loosely coupled to Study models via text fields.
# -----------------------------------------------------------------------------

class JobCard(models.Model):
    """
    The main Job Card. 
    Fields are distinct text inputs to allow manual entry if master lists is missing.
    """
    # Bill Number (Auto-generated)
    bill_number = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True,
        null=True,
        help_text="Auto-generated bill number (e.g. JB-26-001)"
    )
    
    # Dates
    admitted_date = models.DateField()
    discharged_date = models.DateField(blank=True, null=True, help_text="Auto-filled when job is marked as delivered")
    
    # Delivery Status (separate from planning date)
    delivered = models.BooleanField(default=False, help_text="Actually delivered (marked via Delivered button)")
    
    # On Hold Status (for jobs waiting for parts or paused)
    on_hold = models.BooleanField(default=False, help_text="Job is on hold (waiting for parts, etc.)")


    # Vehicle Details (Text fields with Autocomplete)
    brand_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50)
    mileage = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. 50000 or 50k")

    # NEW: Car Color
    COLOR_CHOICES = [
        ('Black', 'Black'),
        ('White', 'White'),
        ('Silver', 'Silver'),
        ('Grey', 'Grey'),
        ('Red', 'Red'),
        ('Light Blue', 'Light Blue'),
        ('Blue', 'Blue'),
        ('Dark Blue', 'Dark Blue'),
        ('Yellow', 'Yellow'),
        ('Light Green', 'Light Green'),
        ('Green', 'Green'),
        ('Dark Green', 'Dark Green'),
        ('Brown', 'Brown'),
        ('Dark Brown', 'Dark Brown'),
        ('Other', 'Other'),
    ]
    car_color = models.CharField(max_length=50, choices=COLOR_CHOICES, blank=True, null=True)
    car_color_other = models.CharField(max_length=100, blank=True, null=True, help_text="Specific color name if 'Other' is selected")

    # Customer Details
    customer_name = models.CharField(max_length=150, blank=True, null=True)
    customer_contact = models.CharField(max_length=20, blank=True, null=True)

    # Assignment
    lead_mechanic = models.ForeignKey(Mechanic, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_cards', help_text="The main mechanic assigned to this job")

    # Financials (NEW)
    received_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Amount actually received from customer")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Internal discount tracking (calculated on Paid status)")
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending (Unpaid)'),
        ('PAID', 'Fully Paid'),
        ('PARTIAL', 'Partially Paid'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI / QR Code'),
        ('CARD', 'Credit/Debit Card'),
        ('TRANSFER', 'Bank Transfer'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Auto-generate bill number if not set.
        Thread-safe implementation to prevent duplicate numbers
        when multiple users create job cards simultaneously.
        """
        from django.db import transaction
        
        if not self.bill_number:
            with transaction.atomic():
                # Get year (2 digits)
                year = str(self.admitted_date.year)[2:]  # 2026 → "26"
                
                # Lock and count existing bills for this year
                # select_for_update() prevents race conditions
                last_job = JobCard.objects.select_for_update().filter(
                    bill_number__startswith=f'JB-{year}-'
                ).order_by('-bill_number').first()
                
                if last_job and last_job.bill_number:
                    # Extract number from last bill (e.g., "JB-26-005" → 5)
                    try:
                        last_num = int(last_job.bill_number.split('-')[-1])
                        next_num = last_num + 1
                    except (ValueError, IndexError):
                        # Fallback if bill number format is unexpected
                        next_num = JobCard.objects.filter(
                            bill_number__startswith=f'JB-{year}-'
                        ).count() + 1
                else:
                    # First bill of the year
                    next_num = 1
                
                # Create bill number (pad with zeros)
                self.bill_number = f'JB-{year}-{str(next_num).zfill(3)}'
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-updated_at'] # Newest jobs first

    def __str__(self):
        return f"{self.bill_number or f'#{self.id}'} - {self.registration_number}"

    @property
    def get_car_color_hex(self):
        """Returns the CSS/Hex color code for the car_color choice."""
        if self.car_color == 'Other' and self.car_color_other:
            # Check if it looks like a hex code (starts with #)
            if self.car_color_other.startswith('#'):
                return self.car_color_other
        
        mapping = {
            'Black': '#000000',
            'White': '#FFFFFF',
            'Silver': '#C0C0C0',
            'Grey': '#9E9E9E',
            'Red': '#F44336',
            'Light Blue': '#81D4FA',
            'Blue': '#2196F3',
            'Dark Blue': '#1565C0',
            'Yellow': '#FFEB3B',
            'Light Green': '#81C784',
            'Green': '#4CAF50',
            'Dark Green': '#2E7D32',
            'Brown': '#795548',
            'Dark Brown': '#4E342E',
        }
        return mapping.get(self.car_color, '#CED4DA')

    @property
    def get_car_color_display(self):
        """Returns the color name (either standard choice or 'Other' text)."""
        if self.car_color == 'Other':
            return self.car_color_other or 'Other'
        return self.car_color or 'Unknown'

    @property
    def get_total_amount(self):
        """Calculates total bill amount (Spares + Labour)."""
        spare_total = sum(item.total_price or 0 for item in self.spares.all())
        labour_total = sum(item.amount or 0 for item in self.labours.all())
        return spare_total + labour_total

    @property
    def get_balance_amount(self):
        """Calculates remaining balance."""
        return max(0, self.get_total_amount - (self.received_amount or 0))

    @property
    def get_completion_percentage(self):
        """
        Calculates completion percentage based on FIXED concerns.
        Returns a dictionary with 'percentage' and 'total'.
        """
        total = self.concerns.count()
        if total == 0:
            return 0
        fixed = self.concerns.filter(status='FIXED').count()
        return int((fixed / total) * 100)


class JobCardConcern(models.Model):
    """
    Specific concerns reported by the customer for a specific Job Card.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('WORKING', 'Working'),
        ('FIXED', 'Fixed'),
    ]

    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='concerns')
    concern_text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def save(self, *args, **kwargs):
        if self.concern_text:
            self.concern_text = self.concern_text.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.concern_text[:50]} ({self.get_status_display()})"


class JobCardSpareItem(models.Model):
    """
    Spare parts used in the job.
    Tracks ordering workflow with shop and dates.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ORDERED', 'Ordered'),
        ('RECEIVED', 'Received'),
    ]

    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='spares')
    spare_part_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    quantity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Pricing (unit_price = shop cost, total_price = customer price with markup)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Shop price (cost)")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Customer price (with markup)")
    
    # Order tracking (NEW)
    shop_name = models.CharField(max_length=100, blank=True, null=True, help_text="Shop where part was ordered")
    ordered_date = models.DateField(blank=True, null=True, help_text="Auto-filled when status → ORDERED")
    received_date = models.DateField(blank=True, null=True, help_text="Auto-filled when status → RECEIVED")

    def save(self, *args, **kwargs):
        if self.spare_part_name:
            self.spare_part_name = self.spare_part_name.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.spare_part_name} ({self.quantity})"


class JobCardLabourItem(models.Model):
    """
    Labour charges added to a Job Card (independent of spares).
    """
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='labours')
    job_description = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) 

    def __str__(self):
        return self.job_description
