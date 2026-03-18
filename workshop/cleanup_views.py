from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from .decorators import office_required
from .models import SparePart, ConcernSolution, JobCardSpareItem, JobCardConcern


@office_required
def data_cleanup_view(request):
    """
    Data Cleanup Tool for Office/Owner.
    Shows all spare parts and concerns with their usage counts.
    """
    # Spare Parts: attach usage count directly onto each object
    spares = list(SparePart.objects.all().order_by('name'))
    for spare in spares:
        spare.usage_count = JobCardSpareItem.objects.filter(
            spare_part_name__iexact=spare.name
        ).count()

    # Concerns: attach usage count directly onto each object
    concerns = list(ConcernSolution.objects.all().order_by('concern'))
    for concern in concerns:
        concern.usage_count = JobCardConcern.objects.filter(
            concern_text__iexact=concern.concern
        ).count()

    return render(request, 'workshop/manage/data_cleanup.html', {
        'spares': spares,
        'concerns': concerns,
    })


@office_required
def cleanup_delete_spare(request, spare_id):
    """Delete a spare part from the master list."""
    if request.method == 'POST':
        spare = get_object_or_404(SparePart, pk=spare_id)
        name = spare.name
        spare.delete()
        messages.success(request, f"✅ Spare part '{name}' removed from master list.")
    return redirect('data_cleanup')


@office_required
def cleanup_rename_spare(request, spare_id):
    """
    Rename a spare part — also updates all existing job card lines
    that used the old name, so history stays accurate.
    """
    if request.method == 'POST':
        spare = get_object_or_404(SparePart, pk=spare_id)
        new_name = request.POST.get('new_name', '').strip().title()

        if not new_name:
            messages.error(request, "New name cannot be empty.")
            return redirect('data_cleanup')

        # Check if target name already exists (merge scenario)
        existing = SparePart.objects.filter(name__iexact=new_name).exclude(pk=spare_id).first()

        # Update all job card items that used the old name
        old_name = spare.name
        JobCardSpareItem.objects.filter(spare_part_name__iexact=old_name).update(
            spare_part_name=new_name
        )

        if existing:
            # Merge: delete the typo entry, keep the correct one
            spare.delete()
            messages.success(request, f"✅ Merged '{old_name}' → '{new_name}'. All job cards updated.")
        else:
            # Simple rename
            spare.name = new_name
            spare.save()
            messages.success(request, f"✅ Renamed '{old_name}' → '{new_name}'. All job cards updated.")

    return redirect('data_cleanup')


@office_required
def cleanup_delete_concern(request, concern_id):
    """Delete a concern from the master list."""
    if request.method == 'POST':
        concern = get_object_or_404(ConcernSolution, pk=concern_id)
        name = concern.concern[:40]
        concern.delete()
        messages.success(request, f"✅ Concern '{name}...' removed from master list.")
    return redirect('data_cleanup')


@office_required
def cleanup_rename_concern(request, concern_id):
    """
    Rename a concern — also updates all existing job card concern lines.
    """
    if request.method == 'POST':
        concern = get_object_or_404(ConcernSolution, pk=concern_id)
        new_text = request.POST.get('new_name', '').strip()

        if not new_text:
            messages.error(request, "New concern text cannot be empty.")
            return redirect('data_cleanup')

        old_text = concern.concern

        # Update all job card concerns that used the old text
        JobCardConcern.objects.filter(concern_text__iexact=old_text).update(
            concern_text=new_text
        )

        # Check for merge (same concern already exists)
        existing = ConcernSolution.objects.filter(
            concern__iexact=new_text
        ).exclude(pk=concern_id).first()

        if existing:
            concern.delete()
            messages.success(request, f"✅ Merged concern into existing entry. All job cards updated.")
        else:
            concern.concern = new_text
            concern.save()
            messages.success(request, f"✅ Concern renamed. All job cards updated.")

    return redirect('data_cleanup')
