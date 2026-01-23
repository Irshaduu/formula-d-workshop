from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q 
from django.http import HttpResponse

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
    
    from django.db.models import Count, Q
    
    # Get only non-delivered job cards (where delivered=False)
    # Discharge date is just for planning - doesn't control visibility
    # Annotate with concern counts for progress bar
    active_jobcards = JobCard.objects.filter(delivered=False).annotate(
        total_concerns=Count('concerns'),
        fixed_concerns=Count('concerns', filter=Q(concerns__status='FIXED'))
    ).order_by('admitted_date')
    
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
    Create a new job card with formsets for concerns, spares, and labour.
    Admitted date defaults to today but is editable.
    Redirects to edit page after save with success message.
    """
    from datetime import date
    from django.contrib import messages
    
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
                saved_concerns = concern_formset.save()
                saved_spares = spare_formset.save()
                labour_formset.save()
                
                # Auto-learn: Add new concerns to master data
                for concern in saved_concerns:
                    if concern.concern_text and concern.concern_text.strip():
                        ConcernSolution.objects.get_or_create(
                            concern=concern.concern_text.strip()
                        )
                
                # Auto-learn: Add new spare parts to master data
                for spare in saved_spares:
                    if spare.spare_part_name and spare.spare_part_name.strip():
                        SparePart.objects.get_or_create(
                            name=spare.spare_part_name.strip()
                        )
                
                messages.success(request, f'Job card for {jobcard.registration_number} created successfully!')
                return redirect('jobcard_edit', pk=jobcard.pk)
    else:
        # Pre-fill admitted_date with today's date
        form = JobCardForm(initial={'admitted_date': date.today()})
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
    Stays on same page after save with success message.
    """
    from django.contrib import messages
    
    jobcard = get_object_or_404(JobCard, pk=pk)

    if request.method == 'POST':
        form = JobCardForm(request.POST, instance=jobcard)
        concern_formset = JobCardConcernFormSet(request.POST, instance=jobcard, prefix='concerns')
        spare_formset = JobCardSpareFormSet(request.POST, instance=jobcard, prefix='spares')
        labour_formset = JobCardLabourFormSet(request.POST, instance=jobcard, prefix='labours')

        if form.is_valid() and concern_formset.is_valid() and spare_formset.is_valid() and labour_formset.is_valid():
            form.save()
            saved_concerns = concern_formset.save()
            saved_spares = spare_formset.save()
            labour_formset.save()
            
            # Auto-learn: Add new concerns to master data
            for concern in saved_concerns:
                if concern.concern_text and concern.concern_text.strip():
                    ConcernSolution.objects.get_or_create(
                        concern=concern.concern_text.strip()
                    )
            
            # Auto-learn: Add new spare parts to master data
            for spare in saved_spares:
                if spare.spare_part_name and spare.spare_part_name.strip():
                    SparePart.objects.get_or_create(
                        name=spare.spare_part_name.strip()
                    )
            
            messages.success(request, f'Job card for {jobcard.registration_number} updated successfully!')
            return redirect('jobcard_edit', pk=jobcard.pk)
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
    Show delivered vehicles with date range filtering.
    Default: Today's deliveries
    Options: today, week, month, year, all, custom
    """
    from datetime import date, timedelta
    
    # Get filter parameter (default to 'today')
    filter_type = request.GET.get('filter', 'today')
    
    # Base queryset
    delivered_jobcards = JobCard.objects.filter(delivered=True).order_by('-discharged_date')
    
    # Apply date filters
    today = date.today()
    
    if filter_type == 'today':
        delivered_jobcards = delivered_jobcards.filter(discharged_date=today)
    elif filter_type == 'week':
        start_date = today - timedelta(days=7)
        delivered_jobcards = delivered_jobcards.filter(discharged_date__gte=start_date)
    elif filter_type == 'month':
        start_date = today - timedelta(days=30)
        delivered_jobcards = delivered_jobcards.filter(discharged_date__gte=start_date)
    elif filter_type == 'year':
        start_date = today - timedelta(days=365)
        delivered_jobcards = delivered_jobcards.filter(discharged_date__gte=start_date)
    elif filter_type == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            delivered_jobcards = delivered_jobcards.filter(
                discharged_date__gte=start_date,
                discharged_date__lte=end_date
            )
    # 'all' - no filtering
    
    return render(request, 'workshop/delivered/delivered_list.html', {
        'delivered_jobcards': delivered_jobcards,
        'filter_type': filter_type,
    })


def mark_delivered(request, pk):
    """
    Mark job card as delivered.
    Auto-sets discharged_date to today (actual delivery date).
    """
    if request.method == 'POST':
        from datetime import date
        jobcard = get_object_or_404(JobCard, pk=pk)
        jobcard.delivered = True
        jobcard.discharged_date = date.today()
        jobcard.save()
    return redirect('home')


def undo_delivered(request, pk):
    """
    Undo delivery by setting delivered=False and clearing discharged_date.
    """
    if request.method == 'POST':
        jobcard = get_object_or_404(JobCard, pk=pk)
        jobcard.delivered = False
        jobcard.discharged_date = None
        jobcard.save()
    return redirect('delivered_list')


def toggle_hold(request, pk):
    """
    Toggle the on_hold status of a job card.
    Used when waiting for parts or other delays.
    """
    if request.method == 'POST':
        jobcard = get_object_or_404(JobCard, pk=pk)
        jobcard.on_hold = not jobcard.on_hold
        jobcard.save()
    return redirect('home')



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


# ============================================================================
# INVOICE VIEW
# ============================================================================

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required  # Regular login is enough
def invoice_view(request, pk):
    """Display professional invoice for a job card"""
    
    # Check if user is staff/admin
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to view invoices. Contact admin.")
    
    jobcard = get_object_or_404(JobCard, pk=pk)
    
    # Calculate labour subtotal (using correct related name: labours)
    labour_subtotal = sum(
        item.amount or 0 
        for item in jobcard.labours.all()
    )
    
    # Calculate spare parts subtotal (using correct related name: spares)
    spare_subtotal = sum(
        item.total_price or 0 
        for item in jobcard.spares.all()
    )
    
    # Calculate grand total
    grand_total = labour_subtotal + spare_subtotal
    
    return render(request, 'workshop/invoice/invoice_template.html', {
        'jobcard': jobcard,
        'labour_subtotal': labour_subtotal,
        'spare_subtotal': spare_subtotal,
        'grand_total': grand_total,
    })


# ============================================================================
# CAR PROFILES
# ============================================================================

from django.db.models import Count, Max

@login_required
def car_profile_list(request):
    """Show all unique cars (grouped by registration) with filters"""
    
    # Get all unique registrations with their latest job card info
    cars = JobCard.objects.values('registration_number').annotate(
        total_visits=Count('id'),
        latest_date=Max('admitted_date'),
    ).order_by('-latest_date')
    
    # Get full details for each car (from their latest job card)
    car_profiles = []
    for car in cars:
        latest_job = JobCard.objects.filter(
            registration_number=car['registration_number']
        ).order_by('-admitted_date').first()
        
        if latest_job:
            car_profiles.append({
                'registration': car['registration_number'],
                'brand': latest_job.brand_name,
                'model': latest_job.model_name,
                'customer': latest_job.customer_name,
                'total_visits': car['total_visits'],
                'latest_date': car['latest_date'],
            })
    
    # Apply filters if provided
    brand_filter = request.GET.get('brand', '')
    search_query = request.GET.get('q', '')
    
    if brand_filter:
        car_profiles = [c for c in car_profiles if brand_filter.lower() in c['brand'].lower()]
    
    if search_query:
        car_profiles = [c for c in car_profiles if 
            search_query.lower() in c['registration'].lower() or
            search_query.lower() in (c['customer'] or '').lower()
        ]
    
    # Get unique brands for filter dropdown
    all_brands = list(set(c['brand'] for c in car_profiles))
    
    return render(request, 'workshop/car_profiles/car_profile_list.html', {
        'car_profiles': car_profiles,
        'all_brands': sorted(all_brands),
        'brand_filter': brand_filter,
        'search_query': search_query,
    })


@login_required
def car_profile_detail(request, registration):
    """Show all bills for a specific car"""
    
    # Get all job cards for this registration
    bills = JobCard.objects.filter(
        registration_number=registration
    ).order_by('-admitted_date')
    
    if not bills.exists():
        raise Http404("Car not found")
    
    # Get car info from latest job card
    latest = bills.first()
    car_info = {
        'registration': registration,
        'brand': latest.brand_name,
        'model': latest.model_name,
        'customer': latest.customer_name,
    }
    
    return render(request, 'workshop/car_profiles/car_profile_detail.html', {
        'car_info': car_info,
        'bills': bills,
    })



