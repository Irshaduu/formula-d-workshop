from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q 
from django.http import HttpResponse
from django.core.paginator import Paginator

from .models import (
    CarBrand, CarModel, SparePart, ConcernSolution,
    JobCard, JobCardConcern, JobCardSpareItem, JobCardLabourItem
)
from .forms import (
    CarBrandForm, CarModelForm, SparePartForm, ConcernSolutionForm,
    JobCardForm, JobCardConcernFormSet, JobCardSpareFormSet, JobCardLabourFormSet
)
from .decorators import staff_required, office_required, owner_required

# =============================================================================
# 1. CORE SECTION (HOME & JOBS)
# =============================================================================

@staff_required
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
    # Optimized with select_related for lead_mechanic to prevent N+1 queries
    active_jobcards = JobCard.objects.filter(delivered=False).select_related('lead_mechanic').annotate(
        total_concerns=Count('concerns'),
        fixed_concerns=Count('concerns', filter=Q(concerns__status='FIXED'))
    ).order_by('-updated_at')
    
    # Count delivered today
    delivered_count = JobCard.objects.filter(
        delivered=True,
        updated_at__date=date.today()  # When delivered button was clicked
    ).count()

    # Count pending bills (Delivered but not fully paid)
    pending_bills_count = JobCard.objects.filter(
        payment_status__in=['PENDING', 'PARTIAL']
    ).count()
    
    return render(request, 'workshop/dashboard/dashboard_home.html', {
        'active_jobcards': active_jobcards,
        'delivered_count': delivered_count,
        'pending_bills_count': pending_bills_count,
    })


@staff_required
def jobcard_create(request):
    """
    Create a new job card with formsets for concerns, spares, and labour.
    Admitted date defaults to today but is editable.
    Redirects to edit page after save with success message.
    Prevents duplicate job cards with 3-attempt confirmation.
    """
    from datetime import date
    from django.contrib import messages
    
    if request.method == 'POST':
        form = JobCardForm(request.POST)

        if form.is_valid():
            jobcard = form.save(commit=False)
            
            # Check for existing active job card for this vehicle
            registration = jobcard.registration_number.strip().upper()
            existing_job = JobCard.objects.filter(
                registration_number__iexact=registration,
                delivered=False
            ).exclude(pk=jobcard.pk).first()
            
            if existing_job:
                # Get or initialize confirmation counter
                session_key = f'duplicate_confirm_{registration}'
                confirm_count = request.session.get(session_key, 0)
                
                if confirm_count < 2:
                    # Increment counter
                    request.session[session_key] = confirm_count + 1
                    
                    # Build message with vehicle details
                    vehicle_info = f"{existing_job.brand_name} {existing_job.model_name}" if existing_job.brand_name else registration
                    
                    # Show warning message
                    messages.warning(
                        request,
                        f'{vehicle_info} ({registration}) has an active job (not marked Delivered).'
                    )
                    
                    # Don't save, return to form with data
                    concern_formset = JobCardConcernFormSet(request.POST, prefix='concerns')
                    spare_formset = JobCardSpareFormSet(request.POST, prefix='spares')
                    labour_formset = JobCardLabourFormSet(request.POST, prefix='labours')
                    
                    # Fetch master lists for datalists
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
                else:
                    # Third attempt - clear counter and proceed with save
                    del request.session[session_key]
            
            # Formsets initialization for standard save
            concern_formset = JobCardConcernFormSet(request.POST, prefix='concerns')
            spare_formset = JobCardSpareFormSet(request.POST, prefix='spares')
            labour_formset = JobCardLabourFormSet(request.POST, prefix='labours')

            if concern_formset.is_valid() and spare_formset.is_valid() and labour_formset.is_valid():
                jobcard.save()

                # Associate instances with jobcard before saving
                concern_formset.instance = jobcard
                spare_formset.instance = jobcard
                labour_formset.instance = jobcard

                saved_concerns = concern_formset.save()
                saved_spares = spare_formset.save()
                labour_formset.save()
                
                # Auto-learn: Add new concerns to master lists (Case-Insensitive)
                for concern in saved_concerns:
                    if concern.concern_text:
                        text = concern.concern_text.strip()
                        if text and not ConcernSolution.objects.filter(concern__iexact=text).exists():
                            ConcernSolution.objects.create(concern=text)
                
                # Auto-learn: Add new spare parts to master lists (Case-Insensitive)
                for spare in saved_spares:
                    if spare.spare_part_name:
                        name = spare.spare_part_name.strip()
                        if name and not SparePart.objects.filter(name__iexact=name).exists():
                            SparePart.objects.create(name=name)
                
                messages.success(request, f'Job card for {jobcard.registration_number} created successfully!')
                return redirect('jobcard_edit', pk=jobcard.pk)
        else:
            # If form is invalid, we still need to initialize formsets for the context
            concern_formset = JobCardConcernFormSet(request.POST, prefix='concerns')
            spare_formset = JobCardSpareFormSet(request.POST, prefix='spares')
            labour_formset = JobCardLabourFormSet(request.POST, prefix='labours')
    else:
        # Pre-fill admitted_date with today's date
        form = JobCardForm(initial={'admitted_date': date.today()})
        concern_formset = JobCardConcernFormSet(prefix='concerns')
        spare_formset = JobCardSpareFormSet(prefix='spares')
        labour_formset = JobCardLabourFormSet(prefix='labours')

    context = {
        'form': form,
        'concern_formset': concern_formset,
        'spare_formset': spare_formset,
        'labour_formset': labour_formset,
        'is_edit': False,
    }
    return render(request, 'workshop/jobcard/jobcard_form.html', context)



@staff_required
def live_report(request):
    """
    SECTION 2.1: LIVE REPORT - Quick scroll for all roles.
    Shows active jobs, concerns, and spares status.
    """
    from django.db.models import Count, Q
    active_jobs = JobCard.objects.filter(delivered=False).select_related('lead_mechanic').prefetch_related('concerns', 'spares').annotate(
        total_concerns=Count('concerns'),
        fixed_concerns=Count('concerns', filter=Q(concerns__status='FIXED'))
    ).order_by('-updated_at')
    
    return render(request, 'workshop/jobcard/live_report.html', {
        'active_jobs': active_jobs,
    })


@office_required
def jobcard_list(request):
    """
    SECTION 2: JOBS - List of saved job cards.
    Newest first is handled by Model Meta ordering.
    """
    jobcard_list_query = JobCard.objects.all()
    
    q = request.GET.get('q')
    if q:
        jobcard_list_query = jobcard_list_query.filter(
            Q(registration_number__icontains=q) |
            Q(bill_number__icontains=q) |
            Q(brand_name__icontains=q) |
            Q(model_name__icontains=q) |
            Q(customer_name__icontains=q) |
            Q(customer_contact__icontains=q) |
            Q(lead_mechanic__name__icontains=q)
        )
        
    paginator = Paginator(jobcard_list_query, 21)  # Show 21 jobs per page
    
    page_number = request.GET.get('page')
    jobcards = paginator.get_page(page_number)
    
    # AJAX Search: Return only the partial template for thousands-ready performance
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'workshop/jobcard/job_list_partial.html', {'jobcards': jobcards})
    
    return render(request, 'workshop/jobcard/jobcard_list.html', {'jobcards': jobcards})


@staff_required
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
            
            # Auto-learn: Add new concerns to master lists (Case-Insensitive)
            for concern in saved_concerns:
                if concern.concern_text:
                    text = concern.concern_text.strip()
                    if text and not ConcernSolution.objects.filter(concern__iexact=text).exists():
                        ConcernSolution.objects.create(concern=text)
            
            # Auto-learn: Add new spare parts to master lists (Case-Insensitive)
            for spare in saved_spares:
                if spare.spare_part_name:
                    name = spare.spare_part_name.strip()
                    if name and not SparePart.objects.filter(name__iexact=name).exists():
                        SparePart.objects.create(name=name)
            
            messages.success(request, f'Job card for {jobcard.registration_number} updated successfully!')
            
            # Smart Redirect based on original context
            next_url = request.GET.get('next')
            if next_url == 'mini':
                return redirect('live_report')
                
            return redirect('jobcard_edit', pk=jobcard.pk)
    else:
        form = JobCardForm(instance=jobcard)
        concern_formset = JobCardConcernFormSet(instance=jobcard, prefix='concerns')
        spare_formset = JobCardSpareFormSet(instance=jobcard, prefix='spares')
        labour_formset = JobCardLabourFormSet(instance=jobcard, prefix='labours')

    context = {
        'form': form,
        'concern_formset': concern_formset,
        'spare_formset': spare_formset,
        'labour_formset': labour_formset,
        'jobcard': jobcard,
        'is_edit': True,
        'next_url': request.GET.get('next'),
    }
    return render(request, 'workshop/jobcard/jobcard_form.html', context)


@office_required # Office and Owners can delete
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

@office_required
def delivered_list(request):
    """
    Show delivered vehicles with date range filtering and AJAX search.
    """
    from datetime import date, timedelta
    
    # 1. Base Query
    delivered_jobcards = JobCard.objects.filter(delivered=True).order_by('-discharged_date')
    
    # 2. Apply AJAX Search Filters (Registration, Customer, Brand, Model)
    q = request.GET.get('q', '').strip()
    if q:
        delivered_jobcards = delivered_jobcards.filter(
            Q(registration_number__icontains=q) |
            Q(customer_name__icontains=q) |
            Q(brand_name__icontains=q) |
            Q(model_name__icontains=q)
        )
    
    # 3. Apply Date Filters
    filter_type = request.GET.get('filter', 'today')
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
    
    # 4. Pagination
    paginator = Paginator(delivered_jobcards, 21) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'delivered_jobcards': page_obj,
        'filter_type': filter_type,
        'q': q,
        'start_date': start_date if filter_type == 'custom' else '',
        'end_date': end_date if filter_type == 'custom' else '',
    }
    
    # 5. AJAX Return Partial
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'workshop/delivered/delivered_list_partial.html', context)
        
    return render(request, 'workshop/delivered/delivered_list.html', context)

@office_required
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


@office_required
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


@office_required # Only office/owner can toggle hold as it affects planning
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
# 2. MASTER LISTS (CARS, SPARES, CONCERNS)
# =============================================================================

@office_required
def master_lists_home(request):
    """Landing page for Master Lists section (optional, mostly accessed via dropdown)."""
    return render(request, 'workshop/master_lists/master_lists_home.html')

# --- CARS (Brands & Models) ---

@office_required
def brand_list(request):
    """Grid of Car Brands"""
    brands = CarBrand.objects.all()
    return render(request, 'workshop/master_lists/brand_list.html', {'brands': brands})

@office_required
def brand_create(request):
    form = CarBrandForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('brand_list')
    return render(request, 'workshop/master_lists/brand_form.html', {'form': form, 'title': 'Add Brand'})

@office_required
def brand_edit(request, pk):
    brand = get_object_or_404(CarBrand, pk=pk)
    form = CarBrandForm(request.POST or None, request.FILES or None, instance=brand)
    if form.is_valid():
        form.save()
        return redirect('brand_list')
    return render(request, 'workshop/master_lists/brand_form.html', {'form': form, 'title': 'Edit Brand'})

@office_required
def brand_delete(request, pk):
    brand = get_object_or_404(CarBrand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        return redirect('brand_list')
    return render(request, 'workshop/master_lists/brand_confirm_delete.html', {'brand': brand})

@office_required
def brand_model_list(request, brand_id):
    """
    Drilldown: Shows models for a specific brand.
    Used when clicking a Brand Logo in brand_list.
    """
    brand = get_object_or_404(CarBrand, pk=brand_id)
    models = brand.models.all()
    return render(request, 'workshop/master_lists/model_list.html', {'brand': brand, 'models': models})

@office_required
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
        
    return render(request, 'workshop/master_lists/model_form.html', {'form': form, 'title': 'Add Model'})

@office_required
def model_edit(request, pk):
    model = get_object_or_404(CarModel, pk=pk)
    form = CarModelForm(request.POST or None, request.FILES or None, instance=model)
    if form.is_valid():
        form.save()
        return redirect('brand_model_list', brand_id=model.brand.id)
    return render(request, 'workshop/master_lists/model_form.html', {'form': form, 'title': 'Edit Model'})

@office_required
def model_delete(request, pk):
    model = get_object_or_404(CarModel, pk=pk)
    brand_id = model.brand.id
    if request.method == 'POST':
        model.delete()
        return redirect('brand_model_list', brand_id=brand_id)
    return render(request, 'workshop/master_lists/model_confirm_delete.html', {'model': model})

# --- SPARE PARTS ---

@office_required
def spare_list(request):
    spares = SparePart.objects.all()
    return render(request, 'workshop/master_lists/spare_list.html', {'spares': spares})

@office_required
def spare_create(request):
    form = SparePartForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('spare_list')
    return render(request, 'workshop/master_lists/spare_form.html', {'form': form, 'title': 'Add Spare'})

@office_required
def spare_edit(request, pk):
    spare = get_object_or_404(SparePart, pk=pk)
    form = SparePartForm(request.POST or None, instance=spare)
    if form.is_valid():
        form.save()
        return redirect('spare_list')
    return render(request, 'workshop/master_lists/spare_form.html', {'form': form, 'title': 'Edit Spare'})

# --- CONCERNS & SOLUTIONS ---

@office_required
def concern_list(request):
    concerns = ConcernSolution.objects.all()
    return render(request, 'workshop/master_lists/concern_list.html', {'concerns': concerns})

@office_required
def concern_create(request):
    form = ConcernSolutionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('concern_list')
    return render(request, 'workshop/master_lists/concern_form.html', {'form': form, 'title': 'Add Solution'})

@staff_required
def concern_edit(request, pk):
    concern = get_object_or_404(ConcernSolution, pk=pk)
    form = ConcernSolutionForm(request.POST or None, instance=concern)
    if form.is_valid():
        form.save()
        return redirect('concern_list')
    return render(request, 'workshop/master_lists/concern_form.html', {'form': form, 'title': 'Edit Solution'})


# =============================================================================
# 3. AUTOCOMPLETE API
# =============================================================================

@staff_required
def autocomplete_brands(request):
    """Returns list of brand names matching query 'q'."""
    q = request.GET.get('q', '')
    if len(q) < 1:
        return JsonResponse([], safe=False)
    brands = CarBrand.objects.filter(name__icontains=q).values_list('name', flat=True)[:10]
    return JsonResponse(list(brands), safe=False)

@staff_required
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

@staff_required
def autocomplete_spares(request):
    """Returns list of spare names matching query 'q', combining Master List and Inventory."""
    q = request.GET.get('q', '')
    if len(q) < 1:
        return JsonResponse([], safe=False)
        
    results = []
    
    # 1. Search Inventory Items (Highest priority, styled in yellow on frontend)
    from inventory.models import Item
    inventory_items = Item.objects.filter(name__icontains=q).values_list('name', flat=True)[:5]
    for name in inventory_items:
        results.append({"name": name, "source": "inventory"})
        
    # 2. Search Master List Spares
    master_spares = SparePart.objects.filter(name__icontains=q).exclude(name__in=inventory_items).values_list('name', flat=True)[:10]
    for name in master_spares:
        results.append({"name": name, "source": "master"})
        
    return JsonResponse(results, safe=False)

@staff_required
def autocomplete_concerns(request):
    """Returns list of concern texts matching query 'q'."""
    q = request.GET.get('q', '')
    if len(q) < 1:
        return JsonResponse([], safe=False)
    concerns = ConcernSolution.objects.filter(concern__icontains=q).values_list('concern', flat=True)[:10]
    return JsonResponse(list(concerns), safe=False)


# ============================================================================
# INVOICE VIEW
# ============================================================================

from django.http import HttpResponseForbidden

@office_required
def invoice_view(request, pk):
    """Display professional invoice for a job card"""
    
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
    
    # Calculate final totals (NEW LOGIC)
    discount = 0 # Not used for now, or keep as 0
    received = jobcard.received_amount or 0
    balance = jobcard.get_balance_amount
    
    return render(request, 'workshop/invoice/invoice_template.html', {
        'jobcard': jobcard,
        'labour_subtotal': labour_subtotal,
        'spare_subtotal': spare_subtotal,
        'grand_total': grand_total,
        'received': received,
        'balance': balance,
    })


@office_required
def update_bill_status(request, pk):
    """
    Quickly update payment status and received amount from Invoice popup.
    Automatically calculates internal discount if Status is PAID.
    """
    if request.method == 'POST':
        jobcard = get_object_or_404(JobCard, pk=pk)
        received = float(request.POST.get('received_amount', 0))
        method = request.POST.get('payment_method')
        status = request.POST.get('payment_status', 'PAID')

        jobcard.received_amount = received
        jobcard.payment_method = method
        jobcard.payment_status = status
        
        # Calculate internal discount silently for admin reports
        if status == 'PAID':
            total_bill = float(jobcard.get_total_amount)
            jobcard.discount_amount = max(0, total_bill - received)
        else:
            jobcard.discount_amount = 0

        jobcard.save()

        from django.contrib import messages
        messages.success(request, f"Billing updated for {jobcard.registration_number}")
    
    return redirect('invoice_view', pk=pk)


@office_required
def pending_payments_list(request):
    """
    Shows a list of job cards that are not fully paid.
    Highly optimized for 10M+ records using SQL Subqueries & Annotations.
    """
    from django.db.models import Sum, Q, Value, F, OuterRef, Subquery
    from django.db.models.functions import Coalesce
    
    # 1. Base Query with Filtering by Payment Status (Indexed)
    pending_jobs = JobCard.objects.filter(
        payment_status__in=['PENDING', 'PARTIAL']
    )

    # 2. AJAX Search (Registration or Customer Name)
    q = request.GET.get('q', '').strip()
    if q:
        pending_jobs = pending_jobs.filter(
            Q(registration_number__icontains=q) |
            Q(customer_name__icontains=q)
        )

    # 3. SQL Annotations (The Scale Optimizer)
    # Using Subqueries to prevent Cartesian Product/Double Counting when summing 
    # over multiple related tables (Spares & Labours).
    
    from django.db.models import Sum, Q, Value, F, OuterRef, Subquery, DecimalField, ExpressionWrapper
    from django.db.models.functions import Coalesce
    from decimal import Decimal
    
    spares_subquery = JobCardSpareItem.objects.filter(
        job_card=OuterRef('pk')
    ).values('job_card').annotate(
        total=Sum('total_price')
    ).values('total')

    labours_subquery = JobCardLabourItem.objects.filter(
        job_card=OuterRef('pk')
    ).values('job_card').annotate(
        total=Sum('amount')
    ).values('total')

    pending_jobs = pending_jobs.annotate(
        annotated_spares=Coalesce(Subquery(spares_subquery), Value(Decimal('0.0'), output_field=DecimalField())),
        annotated_labour=Coalesce(Subquery(labours_subquery), Value(Decimal('0.0'), output_field=DecimalField()))
    ).annotate(
        total_bill=ExpressionWrapper(
            F('annotated_spares') + F('annotated_labour'),
            output_field=DecimalField()
        )
    ).annotate(
        balance_amount=ExpressionWrapper(
            F('total_bill') - F('received_amount'),
            output_field=DecimalField()
        )
    ).order_by('-admitted_date')

    # 4. Global Grand Total
    total_outstanding = pending_jobs.aggregate(
        total=Sum(F('balance_amount'), output_field=DecimalField())
    )['total'] or 0

    # 5. Pagination (21 items per page)
    paginator = Paginator(pending_jobs, 21)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'pending_jobs': page_obj,
        'total_outstanding': total_outstanding,
        'q': q,
    }

    # 6. AJAX Return Partial
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'workshop/jobcard/pending_payments_partial.html', context)

    return render(request, 'workshop/jobcard/pending_payments.html', context)


# ============================================================================
# CAR PROFILES
# ============================================================================

from django.db.models import Count, Max

@office_required
@office_required
def car_profile_list(request):
    """Show all unique cars (grouped by registration) with optimized queries and AJAX search."""
    # 1. Base Query: Group by registration and get latest activity
    cars_query = JobCard.objects.values('registration_number').annotate(
        total_visits=Count('id'),
        latest_date=Max('admitted_date'),
        latest_id=Max('id')
    ).order_by('-latest_date')

    # 2. Get Filters
    search_query = request.GET.get('q', '')

    # 3. Apply Multi-Field Search (Database Level)
    if search_query:
        cars_query = cars_query.filter(
            Q(registration_number__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(brand_name__icontains=search_query) |
            Q(model_name__icontains=search_query)
        )

    # 4. Pagination (Pro-Active Scaling)
    paginator = Paginator(cars_query, 21)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 5. Fetch Full Details for the current page only (N+1 Resolution)
    # We get the full JobCard objects for the latest_ids on this page
    latest_ids = [car['latest_id'] for car in page_obj]
    
    # Materialize the data into a list of dicts for the template
    # (Using a dict for fast lookup)
    details_map = {
        jc.id: jc for jc in JobCard.objects.filter(id__in=latest_ids)
    }
    
    car_profiles = []
    for car in page_obj:
        jc = details_map.get(car['latest_id'])
        if jc:
            car_profiles.append({
                'registration': car['registration_number'],
                'brand': jc.brand_name,
                'model': jc.model_name,
                'customer': jc.customer_name,
                'total_visits': car['total_visits'],
                'latest_date': car['latest_date'],
            })

    # Get unique brands (no longer used for filter, but keeping for other UI if needed - actually better to remove)
    # all_brands = JobCard.objects.values_list('brand_name', flat=True).distinct().order_by('brand_name')

    context = {
        'car_profiles': car_profiles,
        'page_obj': page_obj,
        'search_query': search_query,
    }

    # AJAX Search: Return only the partial template
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'workshop/car_profiles/car_list_partial.html', context)
    
    return render(request, 'workshop/car_profiles/car_profile_list.html', context)


@office_required
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



