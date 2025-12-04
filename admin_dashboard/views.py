"""
Admin Dashboard views
"""
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from admin_dashboard.services import (
    DashboardService, UserManagementService, ListingManagementService,
    TransactionService, CashoutService, FeeSettingsService, DisputeService
)
from authentication.models import Admin
from affiliates.services import AffiliateService
from affiliates.models import Affiliate
from notifications.services import NotificationService
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
        settings = FeeSettingsService.update_fee_settings(
            minimum_fee=request.data.get('minimumFee'),
            fee_percentage=request.data.get('feePercentage'),
            threshold_amount_1=request.data.get('thresholdAmount1'),
            threshold_amount_2=request.data.get('thresholdAmount2'),
            maximum_fee=request.data.get('maximumFee'),
            transaction_fee_fixed=request.data.get('transactionFeeFixed'),
            default_affiliate_commission_percentage=request.data.get('defaultAffiliateCommissionPercentage')
        )
        
        return Response({
            'success': True,
            'minimumFee': settings.minimum_fee,
            'feePercentage': settings.fee_percentage,
            'thresholdAmount1': settings.threshold_amount_1,
            'thresholdAmount2': settings.threshold_amount_2,
            'maximumFee': settings.maximum_fee,
            'transactionFeeFixed': settings.transaction_fee_fixed,
            'defaultAffiliateCommissionPercentage': settings.default_affiliate_commission_percentage,
            'updatedAt': settings.updated_at.isoformat() if settings.updated_at else None
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


# User Management - Additional Endpoints
@api_view(['GET'])
def get_user_details(request, user_id):
    """Get user details"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user_details = UserManagementService.get_user_details(user_id)
        return Response({
            'success': True,
            'user': user_details
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def reactivate_user(request, user_id):
    """Reactivate user"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        reason = request.data.get('reason')
        user = UserManagementService.reactivate_user(user_id, reason)
        return Response({
            'success': True,
            'message': 'User reactivated successfully',
            'user': {
                'id': str(user.id),
                'status': user.status
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Transaction Management - Additional Endpoints
@api_view(['GET'])
def get_transaction_details(request, transaction_id):
    """Get transaction details"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        transaction_details = TransactionService.get_transaction_details(transaction_id)
        return Response({
            'success': True,
            'transaction': transaction_details
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Cashout Request - Additional Endpoints
@api_view(['GET'])
def get_cashout_details(request, cashout_id):
    """Get cashout request details"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        cashout_details = CashoutService.get_cashout_details(cashout_id)
        return Response({
            'success': True,
            'cashoutRequest': cashout_details
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Dispute Management - Additional Endpoints
@api_view(['GET'])
def get_dispute_details(request, dispute_id):
    """Get dispute details"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        dispute_details = DisputeService.get_dispute_details(dispute_id)
        return Response({
            'success': True,
            'dispute': dispute_details
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def add_dispute_message(request, dispute_id):
    """Add dispute message"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        message = request.data.get('message')
        message_type = request.data.get('type', 'admin_note')
        admin_id = str(request.user.id)
        
        if not message:
            return Response({'success': False, 'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        dispute_message = DisputeService.add_dispute_message(dispute_id, message, message_type, admin_id)
        return Response({
            'success': True,
            'message': 'Message added successfully',
            'dispute_message': dispute_message
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def upload_dispute_evidence(request, dispute_id):
    """Upload dispute evidence"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        if 'file' not in request.FILES:
            return Response({'success': False, 'error': 'File is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # For now, return a placeholder response
        # In future, implement file upload to storage
        file = request.FILES['file']
        description = request.data.get('description', '')
        
        # TODO: Implement file upload to storage (S3, local, etc.)
        # For now, return success with placeholder
        return Response({
            'success': True,
            'message': 'Evidence uploaded successfully',
            'evidence': {
                'id': 'placeholder_id',
                'type': file.content_type.split('/')[0] if file.content_type else 'file',
                'url': f'/media/disputes/{dispute_id}/{file.name}',
                'description': description,
                'uploaded_at': datetime.utcnow().isoformat(),
                'uploaded_by': {
                    'id': str(request.user.id),
                    'name': 'Admin User'
                }
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Dashboard - Additional Endpoints
@api_view(['GET'])
def get_recent_activities(request):
    """Get recent activities"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        limit = int(request.GET.get('limit', 10))
        activity_type = request.GET.get('type')
        
        activities = DashboardService.get_recent_activities(limit, activity_type)
        return Response({
            'success': True,
            'activities': activities
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Fee Settings - Additional Endpoints
@api_view(['GET'])
def calculate_fee(request):
    """Calculate fee for a transaction amount"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        amount = request.GET.get('amount')
        if not amount:
            return Response({'success': False, 'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        amount = float(amount)
        if amount <= 0:
            return Response({'success': False, 'error': 'Amount must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
        
        calculation = FeeSettingsService.calculate_fee(amount)
        return Response({
            'success': True,
            'calculation': calculation
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# General Admin APIs
@api_view(['GET'])
def get_admin_profile(request):
    """Get admin profile"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        admin = request.user
        return Response({
            'success': True,
            'admin': {
                'id': str(admin.id),
                'name': admin.name,
                'email': admin.email,
                'role': admin.role,
                'profile_image': admin.profile_image or '',
                'created_at': admin.created_at.isoformat() if hasattr(admin, 'created_at') and admin.created_at else None,
                'last_login': None  # Add if available
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_admin_profile(request):
    """Update admin profile"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        admin = request.user
        
        if 'name' in request.data:
            admin.name = request.data['name']
        if 'profile_image_url' in request.data:
            admin.profile_image = request.data['profile_image_url']
        
        admin.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'admin': {
                'id': str(admin.id),
                'name': admin.name,
                'email': admin.email,
                'profile_image': admin.profile_image or ''
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def change_admin_password(request):
    """Change admin password"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from authentication.services import AuthService
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            return Response({'success': False, 'error': 'All password fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'success': False, 'error': 'New passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = request.user
        
        # Verify current password
        if not AuthService.verify_password(current_password, admin.password_hash):
            return Response({'success': False, 'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update password
        admin.password_hash = AuthService.hash_password(new_password)
        admin.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_activity_logs(request):
    """Get activity logs"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from admin_dashboard.models import ActivityLog
        
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        action = request.GET.get('action')
        from_date = request.GET.get('fromDate')
        to_date = request.GET.get('toDate')
        
        query = ActivityLog.objects()
        
        if action:
            query = query.filter(activity_type=action)
        if from_date:
            from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            query = query.filter(date__gte=from_date_obj)
        if to_date:
            to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            query = query.filter(date__lte=to_date_obj)
        
        total = query.count()
        skip = (page - 1) * limit
        logs = query.order_by('-date').skip(skip).limit(limit)
        
        logs_list = []
        for log in logs:
            logs_list.append({
                'id': str(log.id),
                'admin': {
                    'id': 'system',  # Add if available in ActivityLog model
                    'name': 'System'
                },
                'action': log.activity_type,
                'target_type': 'system',  # Add if available
                'target_id': None,  # Add if available
                'details': log.details or '',
                'date': log.date.isoformat()
            })
        
        return Response({
            'success': True,
            'activityLogs': logs_list,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Affiliate Management - Additional Endpoints
@api_view(['GET'])
def get_affiliate_details(request, affiliate_id):
    """Get affiliate details"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        affiliate = Affiliate.objects(id=affiliate_id).first()
        if not affiliate:
            return Response({'success': False, 'error': 'Affiliate not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get transaction history
        transactions, _ = AffiliateService.get_affiliate_transactions(affiliate_id, 1, 10)
        
        # Format affiliate data
        from affiliates.views import format_affiliate_response
        affiliate_data = format_affiliate_response(affiliate, request)
        affiliate_data['transaction_history'] = transactions
        
        return Response({
            'success': True,
            'affiliate': affiliate_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def toggle_affiliate_status(request, affiliate_id):
    """Toggle affiliate status"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        status_value = request.data.get('status')
        if status_value not in ['active', 'deactivated']:
            return Response({'success': False, 'error': 'Invalid status. Must be "active" or "deactivated"'}, status=status.HTTP_400_BAD_REQUEST)
        
        affiliate = Affiliate.objects(id=affiliate_id).first()
        if not affiliate:
            return Response({'success': False, 'error': 'Affiliate not found'}, status=status.HTTP_404_NOT_FOUND)
        
        affiliate.status = status_value
        affiliate.save()
        
        # Send notification if affiliate is deactivated
        if status_value == 'deactivated':
            try:
                from notifications.notification_helper import NotificationHelper
                NotificationHelper.send_affiliate_account_suspended(str(affiliate.id))
                NotificationHelper.send_policy_violation_warning(str(affiliate.id), 'affiliate')
            except Exception as e:
                import logging
                logging.error(f"Error sending affiliate deactivation notifications: {str(e)}")
        
        return Response({
            'success': True,
            'message': 'Affiliate status updated',
            'affiliate': {
                'id': str(affiliate.id),
                'status': affiliate.status
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Notification Management - Additional Endpoints
@api_view(['PUT'])
def toggle_notification_status(request, notification_id):
    """Toggle notification status"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        active = request.data.get('active')
        if active is None:
            return Response({'success': False, 'error': 'active field is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        notification = NotificationService.update_notification(notification_id, None, None, active)
        
        return Response({
            'success': True,
            'message': 'Notification status updated',
            'notification': {
                'id': str(notification.id),
                'active': notification.active
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_notification_templates(request):
    """Get notification templates"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Return predefined templates
        templates = [
            {
                'key': 'welcome_message',
                'name': 'Welcome Message',
                'description': 'Template for welcoming new users',
                'variables': ['user_name', 'platform_name'],
                'example': 'Welcome {{user_name}} to {{platform_name}}!'
            },
            {
                'key': 'order_confirmation',
                'name': 'Order Confirmation',
                'description': 'Template for order confirmation',
                'variables': ['order_id', 'item_name', 'total_amount'],
                'example': 'Your order {{order_id}} for {{item_name}} has been confirmed. Total: {{total_amount}}'
            },
            {
                'key': 'order_shipped',
                'name': 'Order Shipped',
                'description': 'Template for order shipment notification',
                'variables': ['order_id', 'tracking_number'],
                'example': 'Your order {{order_id}} has been shipped. Tracking: {{tracking_number}}'
            },
            {
                'key': 'payment_received',
                'name': 'Payment Received',
                'description': 'Template for payment received notification',
                'variables': ['amount', 'order_id'],
                'example': 'Payment of {{amount}} received for order {{order_id}}'
            }
        ]
        
        return Response({
            'success': True,
            'templates': templates
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

