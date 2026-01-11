from django.contrib import admin
from .models import (
    CarBrand,
    CarModel,
    SparePart,
    ConcernSolution,
    JobCard,
    JobCardConcern,
    JobCardSpareItem
)


# -------------------------
# STUDY SECTION
# -------------------------

@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'created_at')
    list_filter = ('brand',)
    search_fields = ('name', 'brand__name')
    ordering = ('brand__name', 'name')


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(ConcernSolution)
class ConcernSolutionAdmin(admin.ModelAdmin):
    list_display = ('concern', 'solution', 'created_at')
    search_fields = ('concern', 'solution')
    ordering = ('-created_at',)


# -------------------------
# JOB CARD SECTION
# -------------------------

class JobCardConcernInline(admin.TabularInline):
    model = JobCardConcern
    extra = 1


class JobCardSpareItemInline(admin.TabularInline):
    model = JobCardSpareItem
    extra = 1


@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display = (
        'registration_number',
        'customer_name',
        'brand_name',
        'model_name',
        'updated_at'
    )
    list_filter = ('brand_name',)
    search_fields = (
        'registration_number',
        'customer_name',
        'brand_name',
        'model_name'
    )
    ordering = ('-updated_at',)
    date_hierarchy = 'updated_at'

    inlines = [JobCardConcernInline, JobCardSpareItemInline]
