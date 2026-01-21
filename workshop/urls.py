from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # ------------------
    # SECTION 1: HOME (Job Card Entry)
    # ------------------
    path('', views.home, name='home'),
    path('jobcards/create/', views.jobcard_create, name='jobcard_create'),

    # ------------------
    # SECTION 2: JOBS (Review)
    # ------------------
    path('jobcards/', views.jobcard_list, name='jobcard_list'),
    path('jobcards/<int:pk>/edit/', views.jobcard_edit, name='jobcard_edit'),
    path('jobcards/<int:pk>/delete/', views.jobcard_delete, name='jobcard_delete'),

    # ------------------
    # NEW: DELIVERED (Workshop Dashboard)
    # ------------------
    path('delivered/', views.delivered_list, name='delivered_list'),
    path('jobcards/<int:pk>/deliver/', views.mark_delivered, name='mark_delivered'),
    path('jobcards/<int:pk>/undo-deliver/', views.undo_delivered, name='undo_delivered'),
    path('jobcards/<int:pk>/toggle-hold/', views.toggle_hold, name='toggle_hold'),

    # ------------------
    # SECTION 3: STUDY (Master Data)
    # ------------------
    path('study/', views.study_home, name='study_home'),

    # 3A. Cars (Brand -> Models Drilldown)
    path('study/brands/', views.brand_list, name='brand_list'),
    path('study/brands/add/', views.brand_create, name='brand_add'),
    path('study/brands/<int:brand_id>/models/', views.brand_model_list, name='brand_model_list'),
    
    # Model Management
    path('study/models/add/', views.model_create, name='model_add_generic'), # Fallback
    path('study/brands/<int:brand_id>/models/add/', views.model_create, name='model_add'), # Context aware
    path('study/models/<int:pk>/edit/', views.model_edit, name='model_edit'),

    # 3B. Spares
    path('study/spares/', views.spare_list, name='spare_list'),
    path('study/spares/add/', views.spare_create, name='spare_add'),
    path('study/spares/<int:pk>/edit/', views.spare_edit, name='spare_edit'),

    # 3C. Concerns & Solutions
    path('study/concerns/', views.concern_list, name='concern_list'),
    path('study/concerns/add/', views.concern_create, name='concern_add'),
    path('study/concerns/<int:pk>/edit/', views.concern_edit, name='concern_edit'),

    # ------------------
    # API: AUTOCOMPLETE
    # ------------------
    path('api/autocomplete/brands/', views.autocomplete_brands, name='autocomplete_brands'),
    path('api/autocomplete/models/', views.autocomplete_models, name='autocomplete_models'),
    path('api/autocomplete/spares/', views.autocomplete_spares, name='autocomplete_spares'),

    # ------------------
    # CAR PROFILES
    # ------------------
    path('car-profiles/', views.car_profile_list, name='car_profile_list'),
    path('car-profiles/<str:registration>/', views.car_profile_detail, name='car_profile_detail'),

    # ------------------
    # INVOICE
    # ------------------
    path('invoice/<int:pk>/', views.invoice_view, name='invoice_view'),

    # ------------------
    # AUTH: LOGIN/LOGOUT
    # ------------------
    path('login/', auth_views.LoginView.as_view(template_name='workshop/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
