# meinplugin/urls.py
from django.urls import path
from . import views

# Define URL patterns for the loan plugin
urlpatterns = [
    # List all loans (maps to 'plugin:loan:loan_list')
    path('', views.LoanListView.as_view(), name='loan_list'),

    # Create a new loan (maps to 'plugin:loan:loan_create')
    path('new/', views.LoanCreateView.as_view(), name='loan_create'),

    # View details of a specific loan (maps to 'plugin:loan:loan_detail')
    path('<int:pk>/', views.LoanDetailView.as_view(), name='loan_detail'),

    # TODO: Add URLs for specific actions if needed, e.g.:
    # path('<int:pk>/add_item/', views.LoanAddItemView.as_view(), name='loan_add_item'),
    # path('item/<int:item_pk>/return/', views.LoanReturnItemView.as_view(), name='loan_return_item'),
]