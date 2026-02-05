from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # Landing and Authentication
    path('', views.landing_page, name='landing_page'),
    path('start/', views.role_selection, name='role_selection'),
    # Redirect old login URL to allauth login (with Google OAuth)
    path('login/', RedirectView.as_view(pattern_name='account_login', permanent=False), name='login'),
    path('logout/', RedirectView.as_view(pattern_name='account_logout', permanent=False), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs (using 'manage' to avoid conflict with Django admin)
    path('manage/login/', views.admin_login, name='admin_login'),  # Admin-only login (no Google OAuth)
    path('manage/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # User Management
    path('manage/users/', views.user_list, name='user_list'),
    path('manage/users/create/', views.user_create, name='user_create'),
    path('manage/users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('manage/users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # Payment Management
    path('manage/payments/', views.payment_list, name='payment_list'),
    path('manage/payments/create/', views.payment_create, name='payment_create'),
    path('manage/payments/<int:payment_id>/edit/', views.payment_edit, name='payment_edit'),
    path('manage/payments/<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),
    path('manage/payments/<int:payment_id>/remind/', views.send_payment_reminder, name='send_payment_reminder'),
    
    # Grocery Management
    path('manage/groceries/', views.grocery_list, name='grocery_list'),
    path('manage/groceries/create/', views.grocery_create, name='grocery_create'),
    path('manage/groceries/<int:grocery_id>/edit/', views.grocery_edit, name='grocery_edit'),
    path('manage/groceries/<int:grocery_id>/delete/', views.grocery_delete, name='grocery_delete'),
    
    # Fixed Expense Management
    path('manage/expenses/', views.expense_list, name='expense_list'),
    path('manage/expenses/create/', views.expense_create, name='expense_create'),
    path('manage/expenses/<int:expense_id>/edit/', views.expense_edit, name='expense_edit'),
    path('manage/expenses/<int:expense_id>/delete/', views.expense_delete, name='expense_delete'),
    
    # Message Management
    path('manage/messages/', views.admin_messages, name='admin_messages'),
    path('manage/messages/<int:message_id>/resolve/', views.message_resolve, name='message_resolve'),
    path('manage/messages/<int:message_id>/reply/', views.message_reply, name='message_reply'),
    
    # Reports
    path('manage/reports/monthly/', views.monthly_report, name='monthly_report'),
    
    # Meal Calendar
    path('manage/meals/', views.meal_calendar, name='meal_calendar'),
    path('manage/meals/create/', views.meal_plan_create, name='meal_plan_create'),
    path('manage/meals/<int:plan_id>/edit/', views.meal_plan_edit, name='meal_plan_edit'),
    path('manage/meals/<int:plan_id>/delete/', views.meal_plan_delete, name='meal_plan_delete'),
    
    # User URLs
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/payment/', views.user_payment, name='user_payment'),
    path('user/messages/', views.user_messages_list, name='user_messages_list'),
    path('user/messages/send/', views.user_send_message, name='user_send_message'),
    path('user/messages/<int:message_id>/reply/', views.user_message_reply, name='user_message_reply'),
    path('user/meals/', views.user_meal_calendar, name='user_meal_calendar'),
    path('user/receipt/', views.user_receipt, name='user_receipt'),
    path('user/data/', views.transparent_data, name='transparent_data'),
    path('user/save-theme-preference/', views.save_theme_preference, name='save_theme_preference'),
    path('user/profile-settings/', views.profile_settings, name='profile_settings'),
    
    # Excel Exports
    path('manage/export/payments/', views.export_payments_excel, name='export_payments_excel'),
    path('manage/export/groceries/', views.export_groceries_excel, name='export_groceries_excel'),
    path('manage/export/monthly-report/', views.export_monthly_report_excel, name='export_monthly_report_excel'),
    
    # Password Reset - Custom view to handle registered/unregistered users
    path('password-reset/', views.custom_password_reset, name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # Settings
    path('user/settings/', views.user_settings, name='user_settings'),
    path('manage/settings/', views.admin_settings, name='admin_settings'),
]
