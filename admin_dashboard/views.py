"""
Admin Dashboard views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from admin_dashboard.services import (
    DashboardService, UserManagementService, ListingManagementService,
    TransactionService, CashoutService, FeeSettingsService, DisputeService
)
from authentication.models import Admin


def check_admin(request):
    """Check if user is admin"""
    if not hasattr(request.user, 'role') or request.user.role != 'admin':
        return False
    return True


@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard stats"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        stats = DashboardService.get_dashboard_stats()
        return Response({'success': True, **stats}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def revenue_trends(request):
    """Get revenue trends"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        trends = DashboardService.get_revenue_trends()
        return Response({'success': True, **trends}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def sales_over_time(request):
    """Get sales over time"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        sales = DashboardService.get_sales_over_time()
        return Response({'success': True, **sales}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listings_status_summary(request):
    """Get listings status summary"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        summary = DashboardService.get_listings_status_summary()
        return Response({'success': True, **summary}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def transaction_types_summary(request):
    """Get transaction types summary"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        summary = DashboardService.get_transaction_types_summary()
        return Response({'success': True, **summary}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def disputes_status(request):
    """Get disputes status"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        status_data = DashboardService.get_disputes_status()
        return Response({'success': True, **status_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def cashout_requests_summary(request):
    """Get cashout requests summary"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        summary = DashboardService.get_cashout_requests_summary()
        return Response({'success': True, **summary}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# User Management
@api_view(['GET'])
def get_users(request):
    """Get all users"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')
        
        users, total = UserManagementService.get_users(page, limit, status_filter)
        
        return Response({
            'success': True,
            'users': users,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def suspend_user(request, user_id):
    """Suspend user"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = UserManagementService.suspend_user(user_id)
        return Response({'success': True, 'message': 'User suspended'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def deactivate_user(request, user_id):
    """Deactivate user"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = UserManagementService.deactivate_user(user_id)
        return Response({'success': True, 'message': 'User deactivated'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_user(request, user_id):
    """Delete user"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        UserManagementService.delete_user(user_id)
        return Response({'success': True, 'message': 'User deleted'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Listing Management
@api_view(['GET'])
def get_listings(request):
    """Get all listings"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')
        
        listings, total = ListingManagementService.get_listings(page, limit, status_filter)
        
        return Response({
            'success': True,
            'listings': listings,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def approve_listing(request, listing_id):
    """Approve listing"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        listing = ListingManagementService.approve_listing(listing_id)
        return Response({'success': True, 'message': 'Listing approved'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def reject_listing(request, listing_id):
    """Reject listing"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        listing = ListingManagementService.reject_listing(listing_id)
        return Response({'success': True, 'message': 'Listing rejected'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def hide_listing(request, listing_id):
    """Hide listing"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        listing = ListingManagementService.hide_listing(listing_id)
        return Response({'success': True, 'message': 'Listing hidden'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Transactions
@api_view(['GET'])
def get_transactions(request):
    """Get all transactions"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        type_filter = request.GET.get('type')
        
        transactions, total = TransactionService.get_transactions(page, limit, type_filter)
        
        return Response({
            'success': True,
            'transactions': transactions,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Cashout Requests
@api_view(['GET'])
def get_cashout_requests(request):
    """Get cashout requests"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')
        
        requests, total = CashoutService.get_cashout_requests(page, limit, status_filter)
        
        return Response({
            'success': True,
            'cashoutRequests': requests,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def approve_cashout(request, cashout_id):
    """Approve cashout request"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        admin_id = str(request.user.id)
        cashout = CashoutService.approve_cashout(cashout_id, admin_id)
        return Response({'success': True, 'message': 'Cashout approved'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def reject_cashout(request, cashout_id):
    """Reject cashout request"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        admin_id = str(request.user.id)
        reason = request.data.get('reason', '')
        cashout = CashoutService.reject_cashout(cashout_id, admin_id, reason)
        return Response({'success': True, 'message': 'Cashout rejected'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Fee Settings
@api_view(['GET'])
def get_fee_settings(request):
    """Get fee settings"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        settings = FeeSettingsService.get_fee_settings()
        return Response({'success': True, **settings}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_fee_settings(request):
    """Update fee settings"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        dolabb_fee_percentage = request.data.get('Dolabb Fee Percentage')
        transaction_fee_fixed = request.data.get('Transaction Fee (Fixed Amount $)')
        
        settings = FeeSettingsService.update_fee_settings(dolabb_fee_percentage, transaction_fee_fixed)
        
        return Response({
            'success': True,
            'Dolabb Fee Percentage': settings.dolabb_fee_percentage,
            'Transaction Fee (Fixed Amount $)': settings.transaction_fee_fixed
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def fee_collection_summary(request):
    """Get fee collection summary"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from datetime import datetime
        from_date = request.GET.get('fromDate')
        to_date = request.GET.get('toDate')
        
        from_date_obj = datetime.fromisoformat(from_date) if from_date else None
        to_date_obj = datetime.fromisoformat(to_date) if to_date else None
        
        summary = FeeSettingsService.get_fee_collection_summary(from_date_obj, to_date_obj)
        return Response({'success': True, **summary}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Disputes
@api_view(['GET'])
def get_disputes(request):
    """Get disputes"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')
        
        disputes, total = DisputeService.get_disputes(page, limit, status_filter)
        
        return Response({
            'success': True,
            'disputes': disputes,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_dispute(request, dispute_id):
    """Update dispute"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        status_value = request.data.get('status')
        admin_notes = request.data.get('adminNotes')
        resolution = request.data.get('resolution')
        
        dispute = DisputeService.update_dispute_status(dispute_id, status_value, admin_notes, resolution)
        
        return Response({
            'success': True,
            'dispute': {
                'id': str(dispute.id),
                'status': dispute.status,
                'adminNotes': dispute.admin_notes,
                'resolution': dispute.resolution
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def close_dispute(request, dispute_id):
    """Close dispute"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        resolution = request.data.get('resolution', '')
        dispute = DisputeService.close_dispute(dispute_id, resolution)
        
        return Response({
            'success': True,
            'message': 'Dispute closed'
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

