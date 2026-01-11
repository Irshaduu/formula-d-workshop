from django import forms
from django.forms import inlineformset_factory

from .models import (
    CarBrand,
    CarModel,
    SparePart,
    ConcernSolution,
    JobCard,
    JobCardConcern,
    JobCardSpareItem
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
            'customer_name',
            'customer_contact',
        ]
        widgets = {
            'admitted_date': forms.DateInput(attrs={'type': 'date'}),
            'discharged_date': forms.DateInput(attrs={'type': 'date'}),
            # Autocomplete targets - JS will hook into these IDs/Classes
            'brand_name': forms.TextInput(attrs={
                'autocomplete': 'off',
                'class': 'autocomplete-brand' 
            }),
            'model_name': forms.TextInput(attrs={
                'autocomplete': 'off',
                'class': 'autocomplete-model'
            }),
            'registration_number': forms.TextInput(attrs={
                'style': 'text-transform: uppercase;',
                'autocapitalize': 'characters'
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
    extra=1,           # Start with 1 empty row
    can_delete=False,   # "empty rows ignored", no remove button as requested
    widgets={
        'concern_text': forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 1,
            'placeholder': 'Start typing concern...',
            'style': 'resize: none;'
        })
    }
)

# 2. SPARES
# Columns: Part Name | Qty | Unit Price | Labour | Total
JobCardSpareFormSet = inlineformset_factory(
    JobCard,
    JobCardSpareItem,
    fields=['spare_part_name', 'quantity', 'unit_price', 'labour_charge', 'total_price'],
    extra=1,
    can_delete=False,
    widgets={
        'spare_part_name': forms.TextInput(attrs={
            'class': 'form-control autocomplete-spare', # Target for Autocomplete JS
            'autocomplete': 'off',
            'placeholder': 'Part Name'
        }),
        'quantity': forms.NumberInput(attrs={
            'class': 'form-control text-center', 
            'step': '0.1', # Allow decimals
            'placeholder': 'Qty'
        }),
        'unit_price': forms.NumberInput(attrs={
            'class': 'form-control text-end',
            'placeholder': 'Price'
        }),
        'labour_charge': forms.NumberInput(attrs={
            'class': 'form-control text-end',
            'placeholder': 'Labour'
        }),
        'total_price': forms.NumberInput(attrs={
            'class': 'form-control text-end fw-bold',
            'placeholder': 'Total'
        }),
    }
)
