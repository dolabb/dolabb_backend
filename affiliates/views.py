"""
Affiliate views
"""
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from affiliates.services import AffiliateService
from authentication.models import Affiliate
from authentication.services import AuthService
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
    """Request affiliate cashout - deducts amount from available balance immediately"""
    try:
        affiliate_id = str(request.user.id)
        amount = float(request.data.get('amount', 0))
        
        affiliate = Affiliate.objects(id=affiliate_id).first()
        if not affiliate:
            return Response({'success': False, 'error': 'Affiliate not found'}, status=status.HTTP_404_NOT_FOUND)
        
        pending = float(affiliate.pending_earnings or 0)
        if amount > pending:
            return Response({'success': False, 'error': 'Insufficient pending earnings'}, status=status.HTTP_400_BAD_REQUEST)
        
        if amount <= 0:
            return Response({'success': False, 'error': 'Amount must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
        
        from affiliates.models import AffiliatePayoutRequest
        payout = AffiliatePayoutRequest(
            affiliate_id=affiliate_id,
            affiliate_name=affiliate.full_name,
            amount=amount,
            payment_method=request.data.get('paymentMethod', 'Bank Transfer'),
            account_details=affiliate.account_number or ''
        )
        payout.save()
        
        # Deduct amount from pending_earnings (available balance) immediately
        new_pending = max(0, pending - amount)
        affiliate.pending_earnings = str(round(new_pending, 2))
        affiliate.last_activity = datetime.utcnow()
        affiliate.save()
        
        return Response({
            'success': True,
            'message': 'Cashout request submitted successfully. Amount deducted from available balance.',
            'cashoutRequest': {
                'id': str(payout.id),
                'affiliateId': str(affiliate_id),
                'amount': amount,
                'status': payout.status,
                'requestedAt': payout.requested_date.isoformat()
            },
            'updatedBalance': {
                'availableBalance': round(new_pending, 2),
                'pendingEarnings': round(new_pending, 2)
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


# Helper functions for profile views
def get_date_safe(obj, *attrs):
    """Helper function to safely get date"""
    for attr in attrs:
        val = getattr(obj, attr, None)
        if val:
            try:
                return val.isoformat() if hasattr(val, 'isoformat') else str(val)
            except:
                return str(val)
    return ''

def safe_get(obj, attr, default=''):
    """Helper function to safely get attribute"""
    try:
        val = getattr(obj, attr, default)
        return val if val is not None else default
    except:
        return default

def normalize_image_url(url, request):
    """Helper function to normalize profile image URL"""
    if not url or url == '':
        return ''
    # If URL is already absolute, return as is
    if url.startswith('http://') or url.startswith('https://'):
        return url
    # If URL is relative, make it absolute using current request
    if url.startswith('/'):
        return request.build_absolute_uri(url)
    # If URL doesn't start with /, add /media/ prefix if it's a media file
    if 'uploads' in url or 'profiles' in url:
        return request.build_absolute_uri(f'/media/{url}')
    return url

def format_affiliate_response(affiliate, request):
    """Format affiliate data for response"""
    total_earnings = float(affiliate.total_earnings) if affiliate.total_earnings else 0.0
    pending_earnings = float(affiliate.pending_earnings) if affiliate.pending_earnings else 0.0
    paid_earnings = float(affiliate.paid_earnings) if affiliate.paid_earnings else 0.0
    code_usage_count = int(affiliate.code_usage_count) if affiliate.code_usage_count else 0
    commission_rate = float(affiliate.commission_rate) if affiliate.commission_rate else 0.0
    
    return {
        'id': str(affiliate.id),
        'full_name': safe_get(affiliate, 'full_name'),
        'email': safe_get(affiliate, 'email'),
        'phone': safe_get(affiliate, 'phone'),
        'country_code': safe_get(affiliate, 'country_code'),
        'affiliate_code': safe_get(affiliate, 'affiliate_code'),
        'profile_image': normalize_image_url(safe_get(affiliate, 'profile_image') or '', request),
        'totalEarnings': total_earnings,
        'totalCommissions': total_earnings,
        'pendingEarnings': pending_earnings,
        'paidEarnings': paid_earnings,
        'codeUsageCount': code_usage_count,
        'availableBalance': pending_earnings,
        'commission_rate': commission_rate,
        'status': safe_get(affiliate, 'status', 'active'),
        'bank_details': {
            'bank_name': safe_get(affiliate, 'bank_name'),
            'account_number': safe_get(affiliate, 'account_number'),
            'iban': safe_get(affiliate, 'iban'),
            'account_holder_name': safe_get(affiliate, 'account_holder_name')
        },
        'created_at': get_date_safe(affiliate, 'created_at'),
        'last_activity': get_date_safe(affiliate, 'last_activity')
    }


@api_view(['GET'])
def get_my_transactions(request):
    """Get authenticated affiliate's own transactions (earning breakdown)"""
    try:
        affiliate = request.user
        
        # Verify user is an affiliate
        if not affiliate or not hasattr(affiliate, 'affiliate_code'):
            return Response({'success': False, 'error': 'Unauthorized. Affiliate access required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        affiliate_id = str(affiliate.id)
        
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


@api_view(['GET'])
def get_my_cashout_requests(request):
    """Get authenticated affiliate's own cashout request history"""
    try:
        affiliate = request.user
        
        # Verify user is an affiliate
        if not affiliate or not hasattr(affiliate, 'affiliate_code'):
            return Response({'success': False, 'error': 'Unauthorized. Affiliate access required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        affiliate_id = str(affiliate.id)
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')  # Optional: pending, approved, rejected
        
        requests, total = AffiliateService.get_affiliate_payout_requests(
            affiliate_id=affiliate_id,
            page=page,
            limit=limit,
            status_filter=status_filter
        )
        
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


@api_view(['GET'])
def get_earnings_breakdown(request):
    """Get time-based earnings breakdown for graphs (authenticated affiliate only)"""
    try:
        affiliate = request.user
        
        # Verify user is an affiliate
        if not affiliate or not hasattr(affiliate, 'affiliate_code'):
            return Response({'success': False, 'error': 'Unauthorized. Affiliate access required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        affiliate_id = str(affiliate.id)
        
        # Get query parameters
        period = request.GET.get('period', 'monthly').lower()
        if period not in ['daily', 'weekly', 'monthly', 'yearly']:
            period = 'monthly'
        
        limit = int(request.GET.get('limit', 12))
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
        
        # Get breakdown
        result = AffiliateService.get_earnings_breakdown(
            affiliate_id=affiliate_id,
            period=period,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response({
            'success': True,
            **result
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT'])
def affiliate_profile(request):
    """Get or update affiliate profile (authenticated affiliate only)"""
    try:
        affiliate = request.user
        
        # Verify user is an affiliate
        if not affiliate or not hasattr(affiliate, 'affiliate_code'):
            return Response({'success': False, 'error': 'Unauthorized. Affiliate access required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.method == 'GET':
            # GET: Return affiliate profile
            return Response({
                'success': True,
                'affiliate': format_affiliate_response(affiliate, request)
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            # PUT: Update affiliate profile
            data = request.data
            
            # Update allowed fields
            if 'full_name' in data:
                affiliate.full_name = data['full_name']
            if 'phone' in data:
                affiliate.phone = data['phone']
            if 'country_code' in data:
                affiliate.country_code = data['country_code']
            if 'profile_image' in data or 'profile_image_url' in data:
                # Process base64 image if needed
                image_data = data.get('profile_image') or data.get('profile_image_url')
                if image_data:
                    processed_image = AuthService.process_profile_image(image_data, request)
                    affiliate.profile_image = processed_image if processed_image else image_data
            if 'bank_name' in data:
                affiliate.bank_name = data['bank_name']
            if 'account_number' in data:
                affiliate.account_number = data['account_number']
            if 'iban' in data:
                affiliate.iban = data['iban']
            if 'account_holder_name' in data:
                affiliate.account_holder_name = data['account_holder_name']
            
            # Update last activity
            from datetime import datetime
            affiliate.last_activity = datetime.utcnow()
            
            affiliate.save()
            
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'affiliate': format_affiliate_response(affiliate, request)
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        import traceback
        from django.conf import settings
        return Response({
            'success': False, 
            'error': f'Server error: {str(e)}',
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

