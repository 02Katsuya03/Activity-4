from django.urls import path
from .views import LostPageView, LostDashboardView, LostSchool, LostListView, LostViewItem, LostDetailView, LostAddItemView, LostUpdateItemView, LostDeleteItemView
from .views import FoundDashboardView, FoundListView, FoundViewItem, FoundDetailView, FoundAddItemView, FoundUpdateItemView, FoundDeleteItemView
from .views import ClaimDashboardView, ClaimViewItem, ClaimItemListView, ClaimDetailView, ClaimProcedureView, ClaimF2FStatusView, OnlineClaimStatusView, F2FListView, ClaimUsersListView
from .views import IntroPageView, LoginUserView, LoginAdminView, AdminPageView, FoundUsersListView, LostUsersListView
from .views import RegisterUserView, RegisterAdminView
from .views import logout_view, UserPageView, UserHomeView, UserLostAddItemView, UserLostListView, UserLostUpdateItemView, UserLostDeleteItemView, UserLostViewItem, UserLostDetailView
from .views import UserFoundListView, UserFoundAddItemView, UserFoundViewItem, UserFoundUpdateItemView, UserFoundDeleteItemView, UserFoundDetailView, OnlineClaimProcedureView, OnlineListView
from .views import School, SchoolCreateView,  SchoolListView, SchoolUpdateView, SchoolDeleteView
from . import views

urlpatterns = [
    path('', IntroPageView.as_view(), name='intro'),
    path('logout/', logout_view, name='logout'), 
    path('login_user/', LoginUserView.as_view(), name='login_user'),
    path('login_admin/', LoginAdminView.as_view(), name='login_admin'),
    path('register_user/', RegisterUserView.as_view(), name='register_user'),
    path('register_admin/', RegisterAdminView.as_view(), name='register_admin'),
    path('administrator/', AdminPageView.as_view(), name='administrator'),

    path('user/', UserPageView.as_view(), name='user'),
    path('home/', UserHomeView.as_view(), name='user_home'),
    path('user_lostlistview/', UserLostListView.as_view(), name='user_lostlistview'),
    path('user_lostviewitem/', UserLostViewItem.as_view(), name='user_lostviewitem'),
    path('user_lostdetailview/<str:item_id>', UserLostDetailView.as_view(), name='user_lostdetailview'),
    path('user_lostadditem/create', UserLostAddItemView.as_view(), name='user_lostadditem'),
    path('user_lostupdateitem/<str:item_id>/edit', UserLostUpdateItemView.as_view(), name='user_lostupdateitem'),
    path('user_lostdeleteitem/<str:item_id>/delete', UserLostDeleteItemView.as_view(), name='user_lostdeleteitem'),

    path('user_foundlistview/',UserFoundListView.as_view(), name='user_foundlistview'),
    path('user_foundadditem/create', UserFoundAddItemView.as_view(), name='user_foundadditem'),
    path('user_foundviewitem/', UserFoundViewItem.as_view(), name='user_foundviewitem'),
    path('user_founddetailview/<str:item_id>', UserFoundDetailView.as_view(), name='user_founddetailview'),
    path('user_foundupdateitem/<str:item_id>/edit', UserFoundUpdateItemView.as_view(), name='user_foundupdateitem'),
    path('user_founddeleteitem/<str:item_id>/delete', UserFoundDeleteItemView.as_view(), name='user_founddeleteitem'),

    path('user_claimprocedure/<int:item_id>/', OnlineClaimProcedureView.as_view(), name='user_claimprocedure'),
    path('online_claims/', OnlineListView.as_view(), name='user_onlineclaim'),

    path('lost/', LostPageView.as_view(), name='lost'),
    path('lost_dashboard/', LostDashboardView.as_view(), name='lost_dashboard'),
    path('lost_school/', LostSchool.as_view(), name='lost_school'),
    path('lost_listview/', LostListView.as_view(), name='lost_listview'),
    path('lost_viewitem/', LostViewItem.as_view(), name='lost_viewitem'),
    path('lost_detailview/<str:item_id>', LostDetailView.as_view(), name='lost_detailview'),
    path('lost_additem/create', LostAddItemView.as_view(), name='lost_additem'),
    path('lost_updateitem/<str:item_id>/edit', LostUpdateItemView.as_view(), name='lost_updateitem'),
    path('lost_updateitem/<str:item_id>/delete', LostDeleteItemView.as_view(), name='lost_deleteitem'),
    path('users_lost/', LostUsersListView.as_view(), name='lost_userlist'), 
   
   
    path('found_dashboard/', FoundDashboardView.as_view(), name='found_dashboard'),
    path('found_listview/', FoundListView.as_view(), name='found_listview'),
    path('found_viewitem/', FoundViewItem.as_view(), name='found_viewitem'),
    path('found_detailview/<str:item_id>', FoundDetailView.as_view(), name='found_detailview'),
    path('found_additem/create', FoundAddItemView.as_view(), name='found_additem'),
    path('found_updateitem/<str:item_id>/edit', FoundUpdateItemView.as_view(), name='found_updateitem'),
    path('found_updateitem/<str:item_id>/delete', FoundDeleteItemView.as_view(), name='found_deleteitem'),
    path('users_found/', FoundUsersListView.as_view(), name='found_userlist'),

    path('claim_dashboard/', ClaimDashboardView.as_view(), name='claim_dashboard'),
    path('claim_viewitem/', ClaimViewItem.as_view(), name='claim_viewitem'),
    path('claims/', ClaimItemListView.as_view(), name='claim_claimitem'),
    path('f2f_claims/', F2FListView.as_view(), name='claim_f2fclaim'),
    path('claim_detailview/<str:item_id>', ClaimDetailView.as_view(), name='claim_detailview'),
    path('claim-procedure/<int:item_id>/', ClaimProcedureView.as_view(), name='claim_procedure'),
    path('claim_f2fstatus/', ClaimF2FStatusView.as_view(), name='claim_f2fstatus'),
    path('claim_onlinestatus/', OnlineClaimStatusView.as_view(), name='claim_onlinestatus'),
    path('update_f2f_claim/<int:claim_id>/', views.update_f2f_claim_status, name='update_f2f_claim'),
    path('update_online_claim/<int:claim_id>/', views.update_online_claim_status, name='update_online_claim'),
    path('users_claim/', ClaimUsersListView.as_view(), name='claim_userlist'),

    path('school/', School.as_view(), name='school'),
    path('school_addschool/create', SchoolCreateView.as_view(), name='school_addschool'),
    path('schools/', SchoolListView.as_view(), name='school_listview'),
    path('school/update/<int:pk>/edit', SchoolUpdateView.as_view(), name='school_updateschool'),
    path('school/<int:pk>/delete/', SchoolDeleteView.as_view(), name='school_deleteschool'),

]

