"""
Seller views for earnings and payout management
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from products.seller_service import SellerService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_earnings(request):
    """Get seller earnings summary"""
    try:
        # Verify user is a seller
        if not hasattr(request.user, 'role') or request.user.role != 'seller':
            return Response(
                {'success': False, 'error': 'Only sellers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        seller_id = str(request.user.id)
        earnings = SellerService.get_seller_earnings(seller_id)
        
        return Response({
            'success': True,
            'earnings': earnings
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_seller_payout(request):
    """Request a payout"""
    try:
        # Verify user is a seller
        if not hasattr(request.user, 'role') or request.user.role != 'seller':
            return Response(
                {'success': False, 'error': 'Only sellers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        seller_id = str(request.user.id)
        amount = float(request.data.get('amount', 0))
        payment_method = request.data.get('paymentMethod', 'Bank Transfer')
        
        # Validate required fields
        if not amount or amount <= 0:
            return Response(
                {'success': False, 'error': 'Invalid amount. Amount must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not payment_method:
            return Response(
                {'success': False, 'error': 'Payment method is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payout request
        payout_request = SellerService.request_payout(seller_id, amount, payment_method)
        
        return Response({
            'success': True,
            'payoutRequest': {
                'id': str(payout_request.id),
                'sellerId': str(payout_request.seller_id.id),
                'amount': payout_request.amount,
                'status': payout_request.status,
                'paymentMethod': payout_request.payment_method,
                'requestedAt': payout_request.requested_date.isoformat(),
                'processedAt': None,
                'notes': None
            }
        }, status=status.HTTP_201_CREATED)
    
    except ValueError as e:
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_payout_requests(request):
    """Get payout requests history for seller"""
    try:
        # Verify user is a seller
        if not hasattr(request.user, 'role') or request.user.role != 'seller':
            return Response(
                {'success': False, 'error': 'Only sellers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        seller_id = str(request.user.id)
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')  # Optional: 'pending', 'approved', 'rejected'
        
        payout_requests, total = SellerService.get_payout_requests(
            seller_id, page, limit, status_filter
        )
        
        return Response({
            'success': True,
            'payoutRequests': payout_requests,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit if total > 0 else 0,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

