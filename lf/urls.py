from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('check-username/', views.check_username_availability, name='check_username_availability'),
    path('login/profile/', views.profile, name="profile"),
    path('main/',views.main_page, name="main_page"),
    path('submit_answers/', views.submit_answers, name='submit_answers'),
    path('get_claims_and_responses/<int:item_id>/', views.get_claims_and_responses, name='get_claims_and_responses'),
    path('get_item_details/<int:item_id>/', views.get_item_details, name='get_item_details'),
    path('approve_claim/', views.approve_claim, name='approve_claim'),  # Add this line

]
