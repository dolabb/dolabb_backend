"""
Seller service for earnings and payout management
"""
from datetime import datetime
from products.models import Order
from admin_dashboard.models import CashoutRequest
from authentication.models import User


class SellerService:
    """Seller service for earnings and payout management"""
    
    @staticmethod
    def get_seller_earnings(seller_id):
        """
        Calculate seller earnings summary:
        - totalEarnings: Sum of all seller_payout from completed orders
        - totalPayouts: Sum of all approved payout requests
        - pendingPayouts: Sum of all pending payout requests
        - availableBalance: totalEarnings - totalPayouts - pendingPayouts
        """
        # Get all completed orders (payment_status='completed')
        completed_orders = Order.objects(
            seller_id=seller_id,
            payment_status='completed'
        )
        
        # Calculate total earnings from completed sales
        total_earnings = sum(
            float(order.seller_payout) if order.seller_payout else 0.0 
            for order in completed_orders
        )
        
        # Get all payout requests for this seller
        payout_requests = CashoutRequest.objects(seller_id=seller_id)
        
        # Calculate total approved payouts
        total_payouts = sum(
            float(req.amount) if req.status == 'approved' else 0.0
            for req in payout_requests
        )
        
        # Calculate pending payouts
        pending_payouts = sum(
            float(req.amount) if req.status == 'pending' else 0.0
            for req in payout_requests
        )
        
        # Calculate available balance
        available_balance = total_earnings - total_payouts - pending_payouts
        
        # Ensure available balance is not negative
        if available_balance < 0:
            available_balance = 0.0
        
        return {
            'totalEarnings': round(total_earnings, 2),
            'totalPayouts': round(total_payouts, 2),
            'pendingPayouts': round(pending_payouts, 2),
            'availableBalance': round(available_balance, 2)
        }
    
    @staticmethod
    def request_payout(seller_id, amount, payment_method):
        """
        Create a payout request for seller
        Returns the created payout request
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Invalid amount. Amount must be greater than 0")
        
        # Get seller
        seller = User.objects(id=seller_id).first()
        if not seller:
            raise ValueError("Seller not found")
        
        # Get current earnings to validate available balance
        earnings = SellerService.get_seller_earnings(seller_id)
        available_balance = earnings['availableBalance']
        
        # Validate amount doesn't exceed available balance
        if amount > available_balance:
            raise ValueError("Amount exceeds available balance")
        
        # Validate payment method
        valid_methods = ['Bank Transfer', 'PayPal', 'Stripe']
        if payment_method not in valid_methods:
            raise ValueError(f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
        
        # Create payout request
        payout_request = CashoutRequest(
            seller_id=seller_id,
            seller_name=seller.full_name if hasattr(seller, 'full_name') else seller.username,
            amount=amount,
            payment_method=payment_method,
            status='pending'
        )
        payout_request.save()
        
        return payout_request
    
    @staticmethod
    def get_payout_requests(seller_id, page=1, limit=20, status_filter=None):
        """
        Get payout requests for a seller with pagination
        Returns list of payout requests and total count
        """
        query = CashoutRequest.objects(seller_id=seller_id)
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        total = query.count()
        skip = (page - 1) * limit
        requests = query.skip(skip).limit(limit).order_by('-requested_date')
        
        requests_list = []
        for req in requests:
            requests_list.append({
                'id': str(req.id),
                'sellerId': str(req.seller_id.id),
                'amount': req.amount,
                'status': req.status,
                'paymentMethod': req.payment_method,
                'requestedAt': req.requested_date.isoformat(),
                'processedAt': req.reviewed_at.isoformat() if req.reviewed_at else None,
                'notes': req.notes or req.rejection_reason or None
            })
        
        return requests_list, total

