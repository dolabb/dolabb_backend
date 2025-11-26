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
        Calculate seller earnings summary with shipment proof security:
        - totalEarnings: Sum of seller_payout from completed orders WITH shipment_proof uploaded
        - totalPayouts: Sum of all approved payout requests
        - pendingPayouts: Sum of pending payout requests + orders without shipment_proof
        - availableBalance: totalEarnings - totalPayouts - pendingPayouts
        
        Security: Orders without shipment_proof are NOT added to available balance
        until seller uploads shipment proof.
        """
        # Get all completed orders (payment_status='completed')
        completed_orders = Order.objects(
            seller_id=seller_id,
            payment_status='completed'
        )
        
        # Separate orders with and without shipment proof
        orders_with_proof = []
        orders_without_proof = []
        
        for order in completed_orders:
            if order.shipment_proof and order.shipment_proof.strip():
                # Order has shipment proof uploaded
                orders_with_proof.append(order)
            else:
                # Order is pending shipment proof upload
                orders_without_proof.append(order)
        
        # Calculate total earnings ONLY from orders with shipment proof
        # This is the amount that can be withdrawn
        total_earnings = sum(
            float(order.seller_payout) if order.seller_payout else 0.0 
            for order in orders_with_proof
        )
        
        # Calculate pending earnings from orders without shipment proof
        # These are "locked" until shipment proof is uploaded
        pending_shipment_proof_amount = sum(
            float(order.seller_payout) if order.seller_payout else 0.0
            for order in orders_without_proof
        )
        
        # Get all payout requests for this seller
        payout_requests = CashoutRequest.objects(seller_id=seller_id)
        
        # Calculate total approved payouts
        total_payouts = sum(
            float(req.amount) if req.status == 'approved' else 0.0
            for req in payout_requests
        )
        
        # Calculate pending payout requests
        pending_payout_requests = sum(
            float(req.amount) if req.status == 'pending' else 0.0
            for req in payout_requests
        )
        
        # Total pending payouts = pending payout requests + orders waiting for shipment proof
        pending_payouts = pending_payout_requests + pending_shipment_proof_amount
        
        # Calculate available balance (only from orders with shipment proof)
        available_balance = total_earnings - total_payouts - pending_payout_requests
        
        # Ensure available balance is not negative
        if available_balance < 0:
            available_balance = 0.0
        
        return {
            'totalEarnings': round(total_earnings, 2),
            'totalPayouts': round(total_payouts, 2),
            'pendingPayouts': round(pending_payouts, 2),
            'availableBalance': round(available_balance, 2),
            'pendingShipmentProof': round(pending_shipment_proof_amount, 2)  # Additional info
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

