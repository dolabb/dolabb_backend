"""
Affiliate views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from affiliates.services import AffiliateService
from authentication.models import Affiliate
from admin_dashboard.views import check_admin


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_affiliate_code(request):
    """Validate affiliate code"""
    try:
        code = request.data.get('code')
        if not code:
            return Response({'success': False, 'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = AffiliateService.validate_affiliate_code(code)
        return Response({
            'valid': result['valid'],
            'message': result['message'],
            'affiliate': result.get('affiliate')
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def request_cashout(request):
    """Request affiliate cashout"""
    try:
        affiliate_id = str(request.user.id)
        amount = float(request.data.get('amount', 0))
        
        affiliate = Affiliate.objects(id=affiliate_id).first()
        if not affiliate:
            return Response({'success': False, 'error': 'Affiliate not found'}, status=status.HTTP_404_NOT_FOUND)
        
        pending = float(affiliate.pending_earnings or 0)
        if amount > pending:
            return Response({'success': False, 'error': 'Insufficient pending earnings'}, status=status.HTTP_400_BAD_REQUEST)
        
        from affiliates.models import AffiliatePayoutRequest
        payout = AffiliatePayoutRequest(
            affiliate_id=affiliate_id,
            affiliate_name=affiliate.full_name,
            amount=amount,
            payment_method=request.data.get('paymentMethod', 'Bank Transfer'),
            account_details=affiliate.account_number or ''
        )
        payout.save()
        
        return Response({
            'success': True,
            'cashoutRequest': {
                'id': str(payout.id),
                'affiliateId': str(affiliate_id),
                'amount': amount,
                'status': payout.status,
                'requestedAt': payout.requested_date.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Admin views for affiliate management
@api_view(['GET'])
def get_all_affiliates(request):
    """Get all affiliates (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        
        affiliates, total = AffiliateService.get_all_affiliates(page, limit)
        
        return Response({
            'success': True,
            'affiliates': affiliates,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_affiliate_transactions(request, affiliate_id):
    """Get affiliate transactions (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        
        transactions, total = AffiliateService.get_affiliate_transactions(affiliate_id, page, limit)
        
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


@api_view(['PUT'])
def update_commission_rate(request, affiliate_id):
    """Update affiliate commission rate (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        commission_rate = float(request.data.get('commissionRate', 0))
        affiliate = AffiliateService.update_commission_rate(affiliate_id, commission_rate)
        
        return Response({
            'success': True,
            'message': 'Commission rate updated',
            'affiliate': {
                'id': str(affiliate.id),
                'commissionRate': affiliate.commission_rate
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def suspend_affiliate(request, affiliate_id):
    """Suspend affiliate (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        affiliate = AffiliateService.suspend_affiliate(affiliate_id)
        return Response({'success': True, 'message': 'Affiliate suspended'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_payout_requests(request):
    """Get affiliate payout requests (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')
        
        requests, total = AffiliateService.get_payout_requests(page, limit, status_filter)
        
        return Response({
            'success': True,
            'payoutRequests': requests,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def approve_payout(request, payout_id):
    """Approve affiliate payout (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        admin_id = str(request.user.id)
        payout = AffiliateService.approve_payout(payout_id, admin_id)
        return Response({'success': True, 'message': 'Payout approved'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def reject_payout(request, payout_id):
    """Reject affiliate payout (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        admin_id = str(request.user.id)
        reason = request.data.get('reason', '')
        payout = AffiliateService.reject_payout(payout_id, admin_id, reason)
        return Response({'success': True, 'message': 'Payout rejected'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

