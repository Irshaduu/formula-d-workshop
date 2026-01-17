from django import forms
from django.forms import inlineformset_factory

from .models import (
    CarBrand,
    CarModel,
    SparePart,
    ConcernSolution,
    JobCard,
    JobCardConcern,
    JobCardSpareItem,
    JobCardLabourItem
)

# =============================================================================
# MIXINS & WIDGETS
# =============================================================================

class BootstrapFormMixin:
    """
    Mixin to apply Bootstrap 'form-control' class to all fields.
    Crucially, it APPENDS the class to existing classes to preserve custom hooks.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Determine the correct Bootstrap class
            bootstrap_class = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                bootstrap_class = 'form-check-input'
            
            # Get any existing class (e.g., 'autocomplete-brand')
            existing_class = field.widget.attrs.get('class', '')
            
            # Append or set the new class
            if existing_class:
                new_class = f"{existing_class} {bootstrap_class}"
            else:
                new_class = bootstrap_class
            
            # Update the widget attributes
            field.widget.attrs.update({
                'class': new_class,
                'placeholder': field.label
            })


# =============================================================================
# STUDY FORMS
# =============================================================================

class CarBrandForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CarBrand
        fields = ['name', 'logo_image']
        labels = {
            'name': 'Brand Name',
            'logo_image': 'Brand Logo',
        }


class CarModelForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CarModel
        fields = ['brand', 'name', 'sample_image']
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-select'}),
        }


class SparePartForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SparePart
        fields = ['name']


class ConcernSolutionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ConcernSolution
        fields = ['concern', 'solution']
        widgets = {
            'concern': forms.Textarea(attrs={'rows': 2}),
            'solution': forms.Textarea(attrs={'rows': 2}),
        }


# =============================================================================
# JOB CARD FORM (The Core)
# =============================================================================

class JobCardForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = JobCard
        fields = [
            'admitted_date',
            'discharged_date',
            'brand_name',
            'model_name',
            'registration_number',
            'mileage',
            'customer_name',
            'customer_contact',
        ]
        labels = {
            'discharged_date': 'Discharge Date',  # Changed from default 'Discharged Date'
        }
        widgets = {
            'admitted_date': forms.DateInput(attrs={'type': 'date'}),
            'discharged_date': forms.DateInput(attrs={'type': 'date'}),
            # Autocomplete targets - JS will hook into these IDs/Classes
            'brand_name': forms.TextInput(attrs={
                'autocomplete': 'off',
                'class': 'autocomplete-brand',
                'list': 'datalist-brands'
            }),
            'model_name': forms.TextInput(attrs={
                'autocomplete': 'off',
                'class': 'autocomplete-model',
                'list': 'datalist-models'
            }),
            'registration_number': forms.TextInput(attrs={
                'style': 'text-transform: uppercase;',
                'autocapitalize': 'characters'
            }),
            'mileage': forms.TextInput(attrs={
                'placeholder': 'e.g. 50000 or 50k',
                'inputmode': 'numeric' # Suggests numeric keyboard on mobile but allows text
            }),
            'customer_contact': forms.NumberInput(attrs={
                 # Number input triggers numeric keypad on mobile
            })
        }


# =============================================================================
# FORMSETS
# =============================================================================

# 1. CONCERNS
# Simple rows: [ Concern Text ]
JobCardConcernFormSet = inlineformset_factory(
    JobCard,
    JobCardConcern,
    fields=['concern_text'],
    extra=1,            # Start with 1 empty row
    can_delete=True,    # Allow deletion for proper formset validation
    validate_min=False, # Don't require minimum number of forms
    widgets={
        'concern_text': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Start typing concern...',
            'list': 'datalist-concerns'
        })
    }
)

# 2. SPARES
# Columns: Part Name | Qty | Unit Price | Labour | Total
JobCardSpareFormSet = inlineformset_factory(
    JobCard,
    JobCardSpareItem,
    fields=['spare_part_name', 'quantity', 'total_price'],  # Removed unit_price
    extra=0,
    can_delete=True,    # Allow deletion for proper formset validation
    validate_min=False, # Don't require minimum number of forms
    widgets={
        'spare_part_name': forms.TextInput(attrs={
            'class': 'form-control autocomplete-spare',
            'autocomplete': 'off',
            'placeholder': 'Part Name',
            'list': 'datalist-spares'
        }),
        'quantity': forms.TextInput(attrs={  # Changed to TextInput for easy manual entry
            'class': 'form-control text-center',
            'placeholder': 'Qty'
        }),
        'total_price': forms.TextInput(attrs={  # Changed to TextInput to remove spinner arrows
            'class': 'form-control text-end fw-bold',
            'placeholder': 'Total'
        }),
    }
)

# 3. LABOUR (JOBS)
# Columns: Job Description | Amount
JobCardLabourFormSet = inlineformset_factory(
    JobCard,
    JobCardLabourItem,
    fields=['job_description', 'amount'],
    extra=0,
    can_delete=True,    # Allow deletion for proper formset validation
    validate_min=False, # Don't require minimum number of forms
    widgets={
        'job_description': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job Performed',
            'list': 'datalist-spares'  # Same suggestions as spare parts!
        }),
        'amount': forms.TextInput(attrs={  # Changed to TextInput to remove spinner arrows
            'class': 'form-control text-end',
            'placeholder': 'Amount'
        }),
    }
)
