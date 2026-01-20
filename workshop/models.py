from django.db import models

# -----------------------------------------------------------------------------
# 1. STUDY SECTION MODELS
# These models act as the "Master Data" for autocomplete suggestions.
# -----------------------------------------------------------------------------

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
    sample_image = models.ImageField(upload_to='models/', blank=True, null=True)
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
    Knowledge base for common Concerns and their Solutions.
    Renamed from CustomerConcern to avoid confusion with active Job Cards.
    """
    concern = models.TextField(help_text="e.g., Sound when applying brake")
    solution = models.TextField(help_text="e.g., Change brake pads")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.concern[:30]}... | {self.solution[:30]}..."


# -----------------------------------------------------------------------------
# 2. JOB CARD SECTION MODELS
# These handle the daily work. loosely coupled to Study models via text fields.
# -----------------------------------------------------------------------------

class JobCard(models.Model):
    """
    The main Job Card. 
    Fields are distinct text inputs to allow manual entry if master data is missing.
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
    discharged_date = models.DateField(blank=True, null=True, help_text="Planning date - when you plan to deliver")
    
    # Delivery Status (separate from planning date)
    delivered = models.BooleanField(default=False, help_text="Actually delivered (marked via Delivered button)")

    # Vehicle Details (Text fields with Autocomplete)
    brand_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50)
    mileage = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. 50000 or 50k")

    # Customer Details
    customer_name = models.CharField(max_length=150, blank=True, null=True)
    customer_contact = models.CharField(max_length=20, blank=True, null=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Auto-generate bill number if not set"""
        if not self.bill_number:
            # Get year (2 digits)
            year = str(self.admitted_date.year)[2:]  # 2026 → "26"
            
            # Find highest number for this year
            year_jobs = JobCard.objects.filter(
                bill_number__startswith=f'JB-{year}-'
            ).count()
            
            # Next number (pad with zeros)
            next_num = str(year_jobs + 1).zfill(3)  # 1 → "001"
            
            # Create bill number
            self.bill_number = f'JB-{year}-{next_num}'
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-updated_at'] # Newest jobs first

    def __str__(self):
        return f"{self.bill_number or f'#{self.id}'} - {self.registration_number}"


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

    def __str__(self):
        return f"{self.concern_text[:50]} ({self.get_status_display()})"


class JobCardSpareItem(models.Model):
    """
    Spare parts used in the job.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ORDERED', 'Ordered'),
        ('FIXED', 'Fixed'),
    ]

    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='spares')
    spare_part_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    quantity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.spare_part_name} ({self.quantity})"


class JobCardLabourItem(models.Model):
    """
    Labour charges added to a Job Card (independent of spares).
    """
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='labours')
    job_description = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Removed default=0

    def __str__(self):
        return self.job_description



