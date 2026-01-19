from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q 

from .models import (
    CarBrand, CarModel, SparePart, ConcernSolution,
    JobCard, JobCardConcern, JobCardSpareItem, JobCardLabourItem
)
from .forms import (
    CarBrandForm, CarModelForm, SparePartForm, ConcernSolutionForm,
    JobCardForm, JobCardConcernFormSet, JobCardSpareFormSet, JobCardLabourFormSet
)

# =============================================================================
# 1. CORE SECTION (HOME & JOBS)
# =============================================================================

def home(request):
    """
    Dashboard homepage showing all active job cards.
    Discharge date is a planning field, not a filter.
    Cars only move to Delivered when "Delivered" button is clicked.
    """
    from datetime import date
    
    # Get only non-delivered job cards (where delivered=False)
    # Discharge date is just for planning - doesn't control visibility
    active_jobcards = JobCard.objects.filter(delivered=False).order_by('admitted_date')
    
    # Count delivered today
    delivered_count = JobCard.objects.filter(
        delivered=True,
        updated_at__date=date.today()  # When delivered button was clicked
    ).count()
    
    return render(request, 'workshop/dashboard/dashboard_home.html', {
        'active_jobcards': active_jobcards,
        'delivered_count': delivered_count,
    })


def jobcard_create(request):
    """
    Create a new job card (moved from home).
    """
    if request.method == 'POST':
        form = JobCardForm(request.POST)

        if form.is_valid():
            jobcard = form.save(commit=False)

            concern_formset = JobCardConcernFormSet(
                request.POST,
                instance=jobcard,
                prefix='concerns'
            )
            spare_formset = JobCardSpareFormSet(
                request.POST,
                instance=jobcard,
                prefix='spares'
            )
            labour_formset = JobCardLabourFormSet(
                request.POST,
                instance=jobcard,
                prefix='labours'
            )

            if concern_formset.is_valid() and spare_formset.is_valid() and labour_formset.is_valid():
                jobcard.save()
                concern_formset.save()
                spare_formset.save()
                labour_formset.save()
                return redirect('jobcard_list')
    else:
        form = JobCardForm()
        concern_formset = JobCardConcernFormSet(prefix='concerns')
        spare_formset = JobCardSpareFormSet(prefix='spares')
        labour_formset = JobCardLabourFormSet(prefix='labours')

    # Fetch master data for datalists
    brands = CarBrand.objects.all()
    models = CarModel.objects.all()
    spares = SparePart.objects.all()
    concerns = ConcernSolution.objects.all()

    return render(request, 'workshop/jobcard/jobcard_form.html', {
        'form': form,
        'concern_formset': concern_formset,
        'spare_formset': spare_formset,
        'labour_formset': labour_formset,
        'is_edit': False,
        'brands': brands,
        'models': models,
        'spares': spares,
        'concerns': concerns,
    })



def jobcard_list(request):
    """
    SECTION 2: JOBS - List of saved job cards.
    Newest first is handled by Model Meta ordering.
    """
    jobcards = JobCard.objects.all() 
    return render(request, 'workshop/jobcard/jobcard_list.html', {'jobcards': jobcards})


def jobcard_edit(request, pk):
    """
    Edit an existing Job Card. Pre-populates form and formsets.
    """
    jobcard = get_object_or_404(JobCard, pk=pk)

    if request.method == 'POST':
        form = JobCardForm(request.POST, instance=jobcard)
        concern_formset = JobCardConcernFormSet(request.POST, instance=jobcard, prefix='concerns')
        spare_formset = JobCardSpareFormSet(request.POST, instance=jobcard, prefix='spares')
        labour_formset = JobCardLabourFormSet(request.POST, instance=jobcard, prefix='labours')

        if form.is_valid() and concern_formset.is_valid() and spare_formset.is_valid() and labour_formset.is_valid():
            form.save()
            concern_formset.save()
            spare_formset.save()
            labour_formset.save()
            return redirect('jobcard_list')
    else:
        form = JobCardForm(instance=jobcard)
        concern_formset = JobCardConcernFormSet(instance=jobcard, prefix='concerns')
        spare_formset = JobCardSpareFormSet(instance=jobcard, prefix='spares')
        labour_formset = JobCardLabourFormSet(instance=jobcard, prefix='labours')

    # Fetch master data for datalists
    brands = CarBrand.objects.all()
    models = CarModel.objects.all()
    spares = SparePart.objects.all()
    concerns = ConcernSolution.objects.all()

    context = {
        'form': form,
        'concern_formset': concern_formset,
        'spare_formset': spare_formset,
        'labour_formset': labour_formset,
        'jobcard': jobcard,
        'is_edit': True,
        'brands': brands,
        'models': models,
        'spares': spares,
        'concerns': concerns,
    }
    return render(request, 'workshop/jobcard/jobcard_form.html', context)


def jobcard_delete(request, pk):
    """
    Simple confirmation page before deletion.
    """
    jobcard = get_object_or_404(JobCard, pk=pk)
    if request.method == 'POST':
        jobcard.delete()
        return redirect('jobcard_list')
    return render(request, 'workshop/jobcard/jobcard_confirm_delete.html', {'jobcard': jobcard})


# =============================================================================
# NEW: DELIVERED SECTION (Workshop Dashboard)
# =============================================================================

def delivered_list(request):
    """
    Shows all delivered vehicles (delivered=True).
    Ordered by when they were marked as delivered (newest first).
    """
    delivered_jobcards = JobCard.objects.filter(delivered=True).order_by('-updated_at')
    return render(request, 'workshop/delivered/delivered_list.html', {'delivered_jobcards': delivered_jobcards})


def mark_delivered(request, pk):
    """
    Mark a job card as actually delivered.
    Sets delivered=True (discharge_date remains as planning date).
    """
    if request.method == 'POST':
        jobcard = get_object_or_404(JobCard, pk=pk)
        jobcard.delivered = True
        jobcard.save()
    return redirect('home')


def undo_delivered(request, pk):
    """
    Undo delivery by setting delivered=False.
    Discharge date remains unchanged (it's a planning date).
    """
    if request.method == 'POST':
        jobcard = get_object_or_404(JobCard, pk=pk)
        jobcard.delivered = False
        jobcard.save()
    return redirect('delivered_list')


# =============================================================================
# 2. STUDY SECTION (CARS, SPARES, CONCERNS)
# =============================================================================

def study_home(request):
    """Landing page for Study section (optional, mostly accessed via dropdown)."""
    return render(request, 'workshop/study/study_home.html')

# --- CARS (Brands & Models) ---

def brand_list(request):
    """Grid of Car Brands"""
    brands = CarBrand.objects.all()
    return render(request, 'workshop/study/brand_list.html', {'brands': brands})

def brand_create(request):
    form = CarBrandForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('brand_list')
    return render(request, 'workshop/study/brand_form.html', {'form': form, 'title': 'Add Brand'})

def brand_model_list(request, brand_id):
    """
    Drilldown: Shows models for a specific brand.
    Used when clicking a Brand Logo in brand_list.
    """
    brand = get_object_or_404(CarBrand, pk=brand_id)
    models = brand.models.all()
    return render(request, 'workshop/study/model_list.html', {'brand': brand, 'models': models})

def model_create(request, brand_id=None):
    """
    Create a model. 
    If brand_id is passed (from drilldown), pre-select that brand in the form.
    """
    initial = {}
    if brand_id:
        brand = get_object_or_404(CarBrand, pk=brand_id)
        initial['brand'] = brand
    
    form = CarModelForm(request.POST or None, request.FILES or None, initial=initial)
    if form.is_valid():
        model = form.save()
        # Redirect back to the brand model list
        return redirect('brand_model_list', brand_id=model.brand.id)
        
    return render(request, 'workshop/study/model_form.html', {'form': form, 'title': 'Add Model'})

def model_edit(request, pk):
    model = get_object_or_404(CarModel, pk=pk)
    form = CarModelForm(request.POST or None, request.FILES or None, instance=model)
    if form.is_valid():
        form.save()
        return redirect('brand_model_list', brand_id=model.brand.id)
    return render(request, 'workshop/study/model_form.html', {'form': form, 'title': 'Edit Model'})

# --- SPARE PARTS ---

def spare_list(request):
    spares = SparePart.objects.all()
    return render(request, 'workshop/study/spare_list.html', {'spares': spares})

def spare_create(request):
    form = SparePartForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('spare_list')
    return render(request, 'workshop/study/spare_form.html', {'form': form, 'title': 'Add Spare'})

def spare_edit(request, pk):
    spare = get_object_or_404(SparePart, pk=pk)
    form = SparePartForm(request.POST or None, instance=spare)
    if form.is_valid():
        form.save()
        return redirect('spare_list')
    return render(request, 'workshop/study/spare_form.html', {'form': form, 'title': 'Edit Spare'})

# --- CONCERNS & SOLUTIONS ---

def concern_list(request):
    concerns = ConcernSolution.objects.all()
    return render(request, 'workshop/study/concern_list.html', {'concerns': concerns})

def concern_create(request):
    form = ConcernSolutionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('concern_list')
    return render(request, 'workshop/study/concern_form.html', {'form': form, 'title': 'Add Solution'})

def concern_edit(request, pk):
    concern = get_object_or_404(ConcernSolution, pk=pk)
    form = ConcernSolutionForm(request.POST or None, instance=concern)
    if form.is_valid():
        form.save()
        return redirect('concern_list')
    return render(request, 'workshop/study/concern_form.html', {'form': form, 'title': 'Edit Solution'})


# =============================================================================
# 3. AUTOCOMPLETE API
# =============================================================================

def autocomplete_brands(request):
    """Returns list of brand names matching query 'q'."""
    q = request.GET.get('q', '')
    if len(q) < 1:
        return JsonResponse([], safe=False)
    brands = CarBrand.objects.filter(name__icontains=q).values_list('name', flat=True)[:10]
    return JsonResponse(list(brands), safe=False)

def autocomplete_models(request):
    """
    Returns list of model names matching query 'q'.
    Optional 'brand' param filters by brand name.
    """
    q = request.GET.get('q', '')
    brand = request.GET.get('brand', '')
    
    qs = CarModel.objects.filter(name__icontains=q)
    if brand:
        qs = qs.filter(brand__name__icontains=brand)
        
    models = qs.values_list('name', flat=True)[:10]
    return JsonResponse(list(models), safe=False)

def autocomplete_spares(request):
    """Returns list of spare names matching query 'q'."""
    q = request.GET.get('q', '')
    if len(q) < 1:
        return JsonResponse([], safe=False)
    spares = SparePart.objects.filter(name__icontains=q).values_list('name', flat=True)[:10]
    return JsonResponse(list(spares), safe=False)
