"""
Affiliate services
"""
from datetime import datetime
from affiliates.models import AffiliateTransaction, AffiliatePayoutRequest
from authentication.models import Affiliate, User
from products.models import Order


class AffiliateService:
    """Affiliate service"""
    
    @staticmethod
    def validate_affiliate_code(code):
        """Validate affiliate code"""
        affiliate = Affiliate.objects(affiliate_code=code, status='active').first()
        if not affiliate:
            return {
                'valid': False,
                'message': 'Invalid or inactive affiliate code'
            }
        
        return {
            'valid': True,
            'message': 'Valid affiliate code',
            'affiliate': {
                'id': str(affiliate.id),
                'fullName': affiliate.full_name,
                'email': affiliate.email,
                'affiliateCode': affiliate.affiliate_code,
                'commissionRate': affiliate.commission_rate,
                'status': affiliate.status
            }
        }
    
    @staticmethod
    def get_all_affiliates(page=1, limit=20):
        """Get all affiliates"""
        affiliates = Affiliate.objects()
        
        total = affiliates.count()
        skip = (page - 1) * limit
        affiliates = affiliates.skip(skip).limit(limit)
        
        affiliates_list = []
        for affiliate in affiliates:
            # Calculate stats
            transactions = AffiliateTransaction.objects(affiliate_id=affiliate.id)
            total_referrals = transactions.count()
            total_earnings = sum(t.commission_amount for t in transactions)
            
            affiliates_list.append({
                '_id': str(affiliate.id),
                'Affiliatename': affiliate.full_name,
                'Affiliateemail': affiliate.email,
                'commissionRate': affiliate.commission_rate,
                'codeUsageCount': affiliate.code_usage_count,
                'Earnings': {
                    'Total': affiliate.total_earnings,
                    'Pending': affiliate.pending_earnings,
                    'Paid': affiliate.paid_earnings
                },
                'Affiliatestatus': affiliate.status,
                'Last Activity': affiliate.last_activity.isoformat(),
                'stats': {
                    'totalReferrals': total_referrals,
                    'totalEarnings': float(affiliate.total_earnings or 0)
                }
            })
        
        return affiliates_list, total
    
    @staticmethod
    def get_affiliate_transactions(affiliate_id, page=1, limit=20):
        """Get affiliate transactions"""
        transactions = AffiliateTransaction.objects(affiliate_id=affiliate_id)
        
        total = transactions.count()
        skip = (page - 1) * limit
        transactions = transactions.skip(skip).limit(limit)
        
        # Get affiliate stats
        affiliate = Affiliate.objects(id=affiliate_id).first()
        all_transactions = AffiliateTransaction.objects(affiliate_id=affiliate_id)
        total_referrals = all_transactions.count()
        total_earnings = sum(t.commission_amount for t in all_transactions)
        total_sales = all_transactions.count()
        
        transactions_list = []
        for transaction in transactions:
            referred_user = User.objects(id=transaction.referred_user_id.id).first() if transaction.referred_user_id else None
            
            transactions_list.append({
                '_id': str(transaction.id),
                'affiliateId': str(transaction.affiliate_id.id),
                'affiliateName': transaction.affiliate_name,
                'stats': {
                    'totalReferrals': total_referrals,
                    'totalEarnings': total_earnings,
                    'Total Sales': total_sales,
                    'Commission Rate': transaction.commission_rate
                },
                'Transaction ID': str(transaction.transaction_id.id) if transaction.transaction_id else '',
                'date': transaction.date.isoformat(),
                'Referred User Name': transaction.referred_user_name or (referred_user.full_name if referred_user else ''),
                'Referred User Commission': transaction.commission_amount,
                'status': transaction.status
            })
        
        return transactions_list, total
    
    @staticmethod
    def update_commission_rate(affiliate_id, commission_rate):
        """Update affiliate commission rate"""
        affiliate = Affiliate.objects(id=affiliate_id).first()
        if not affiliate:
            raise ValueError("Affiliate not found")
        
        affiliate.commission_rate = str(commission_rate)
        affiliate.save()
        
        return affiliate
    
    @staticmethod
    def suspend_affiliate(affiliate_id):
        """Suspend affiliate"""
        affiliate = Affiliate.objects(id=affiliate_id).first()
        if not affiliate:
            raise ValueError("Affiliate not found")
        
        affiliate.status = 'deactivated'
        affiliate.save()
        
        return affiliate
    
    @staticmethod
    def get_payout_requests(page=1, limit=20, status_filter=None):
        """Get affiliate payout requests"""
        query = AffiliatePayoutRequest.objects()
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        total = query.count()
        skip = (page - 1) * limit
        requests = query.skip(skip).limit(limit)
        
        requests_list = []
        for req in requests:
            requests_list.append({
                '_id': str(req.id),
                'affiliateId': str(req.affiliate_id.id),
                'affiliateName': req.affiliate_name,
                'amount': req.amount,
                'Requested Date': req.requested_date.isoformat(),
                'Payment Method': req.payment_method,
                'Status': req.status,
                'accountDetails': req.account_details,
                'rejectionReason': req.rejection_reason
            })
        
        return requests_list, total
    
    @staticmethod
    def approve_payout(payout_id, admin_id):
        """Approve affiliate payout"""
        payout = AffiliatePayoutRequest.objects(id=payout_id).first()
        if not payout:
            raise ValueError("Payout request not found")
        
        payout.status = 'approved'
        payout.reviewed_at = datetime.utcnow()
        payout.reviewed_by = admin_id
        payout.save()
        
        # Update affiliate earnings
        affiliate = Affiliate.objects(id=payout.affiliate_id.id).first()
        if affiliate:
            paid = float(affiliate.paid_earnings or 0) + payout.amount
            pending = float(affiliate.pending_earnings or 0) - payout.amount
            affiliate.paid_earnings = str(paid)
            affiliate.pending_earnings = str(max(0, pending))
            affiliate.save()
        
        return payout
    
    @staticmethod
    def reject_payout(payout_id, admin_id, reason):
        """Reject affiliate payout"""
        payout = AffiliatePayoutRequest.objects(id=payout_id).first()
        if not payout:
            raise ValueError("Payout request not found")
        
        payout.status = 'rejected'
        payout.rejection_reason = reason
        payout.reviewed_at = datetime.utcnow()
        payout.reviewed_by = admin_id
        payout.save()
        
        return payout

