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
    # Dates
    admitted_date = models.DateField()
    discharged_date = models.DateField(blank=True, null=True)

    # Vehicle Details (Text fields with Autocomplete)
    brand_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50)

    # Customer Details
    customer_name = models.CharField(max_length=150)
    customer_contact = models.CharField(max_length=20)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at'] # Newest jobs first

    def __str__(self):
        return f"{self.registration_number} - {self.customer_name}"


class JobCardConcern(models.Model):
    """
    Specific concerns reported by the customer for a specific Job Card.
    """
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='concerns')
    concern_text = models.TextField()

    def __str__(self):
        return self.concern_text[:50]


class JobCardSpareItem(models.Model):
    """
    Spare parts and labour added to a Job Card.
    All monetary fields are manual entry (Zero logic).
    """
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='spares')

    spare_part_name = models.CharField(max_length=150)
    
    # Changed to DecimalField to allow fractional quantities (e.g. 3.5 liters oil)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, blank=True, null=True)
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    labour_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    def __str__(self):
        return f"{self.spare_part_name} ({self.quantity})"
