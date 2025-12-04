"""
Affiliate services
"""
from datetime import datetime, timedelta
from collections import defaultdict
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
                'affiliateCode': affiliate.affiliate_code,
                'commissionRate': float(affiliate.commission_rate) if affiliate.commission_rate else 0.0,
                'codeUsageCount': int(affiliate.code_usage_count) if affiliate.code_usage_count else 0,
                'Earnings': {
                    'Total': float(affiliate.total_earnings) if affiliate.total_earnings else 0.0,
                    'Pending': float(affiliate.pending_earnings) if affiliate.pending_earnings else 0.0,
                    'Paid': float(affiliate.paid_earnings) if affiliate.paid_earnings else 0.0
                },
                'Affiliatestatus': affiliate.status,
                'Last Activity': affiliate.last_activity.isoformat() if affiliate.last_activity else None,
                'stats': {
                    'totalReferrals': total_referrals,
                    'totalEarnings': float(affiliate.total_earnings or 0),
                    'totalTransactions': total_referrals
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
        """Get affiliate payout requests (admin - all affiliates)"""
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
    def get_affiliate_payout_requests(affiliate_id, page=1, limit=20, status_filter=None):
        """Get payout requests for a specific affiliate"""
        query = AffiliatePayoutRequest.objects(affiliate_id=affiliate_id)
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        total = query.count()
        skip = (page - 1) * limit
        requests = query.skip(skip).limit(limit).order_by('-requested_date')
        
        requests_list = []
        for req in requests:
            requests_list.append({
                'id': str(req.id),
                'affiliateId': str(req.affiliate_id.id),
                'affiliateName': req.affiliate_name,
                'amount': req.amount,
                'requestedDate': req.requested_date.isoformat(),
                'paymentMethod': req.payment_method,
                'status': req.status,
                'accountDetails': req.account_details,
                'rejectionReason': req.rejection_reason,
                'reviewedAt': req.reviewed_at.isoformat() if req.reviewed_at else None,
                'reviewedBy': req.reviewed_by
            })
        
        return requests_list, total
    
    @staticmethod
    def approve_payout(payout_id, admin_id):
        """Approve affiliate payout - move amount from pending to paid earnings"""
        payout = AffiliatePayoutRequest.objects(id=payout_id).first()
        if not payout:
            raise ValueError("Payout request not found")
        
        payout.status = 'approved'
        payout.reviewed_at = datetime.utcnow()
        payout.reviewed_by = admin_id
        payout.save()
        
        # Update affiliate earnings
        # Note: Amount was already deducted from pending_earnings when request was created
        # So we just need to add it to paid_earnings
        affiliate = Affiliate.objects(id=payout.affiliate_id.id).first()
        if affiliate:
            paid = float(affiliate.paid_earnings or 0) + payout.amount
            affiliate.paid_earnings = str(round(paid, 2))
            affiliate.save()
        
        # Send notification to affiliate
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_payout_sent(str(payout.affiliate_id.id), 'affiliate')
        except Exception as e:
            import logging
            logging.error(f"Error sending affiliate payout notification: {str(e)}")
        
        return payout
    
    @staticmethod
    def reject_payout(payout_id, admin_id, reason):
        """Reject affiliate payout - refund amount back to pending_earnings"""
        payout = AffiliatePayoutRequest.objects(id=payout_id).first()
        if not payout:
            raise ValueError("Payout request not found")
        
        payout.status = 'rejected'
        payout.rejection_reason = reason
        payout.reviewed_at = datetime.utcnow()
        payout.reviewed_by = admin_id
        payout.save()
        
        # Refund amount back to pending_earnings (available balance)
        affiliate = Affiliate.objects(id=payout.affiliate_id.id).first()
        if affiliate:
            pending = float(affiliate.pending_earnings or 0) + payout.amount
            affiliate.pending_earnings = str(round(pending, 2))
            affiliate.save()
        
        # Send notification to affiliate
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_payout_failed(str(payout.affiliate_id.id), 'affiliate')
        except Exception as e:
            import logging
            logging.error(f"Error sending affiliate payout failed notification: {str(e)}")
        
        return payout
    
    @staticmethod
    def get_earnings_breakdown(affiliate_id, period='monthly', limit=12, start_date=None, end_date=None):
        """Get time-based earnings breakdown for graphs"""
        affiliate = Affiliate.objects(id=affiliate_id).first()
        if not affiliate:
            raise ValueError("Affiliate not found")
        
        # Get all transactions for this affiliate
        transactions_query = AffiliateTransaction.objects(affiliate_id=affiliate_id)
        
        # Apply date filters if provided
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            transactions_query = transactions_query.filter(date__gte=start_date)
        
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            transactions_query = transactions_query.filter(date__lte=end_date)
        
        transactions = list(transactions_query.order_by('-date'))
        
        # Get summary totals from affiliate (these account for cashouts and are the source of truth)
        total_earnings = float(affiliate.total_earnings) if affiliate.total_earnings else 0.0
        pending_earnings = float(affiliate.pending_earnings) if affiliate.pending_earnings else 0.0
        paid_earnings = float(affiliate.paid_earnings) if affiliate.paid_earnings else 0.0
        
        # Calculate transaction totals for reference (before cashout deductions)
        total_from_transactions = sum(t.commission_amount for t in transactions)
        pending_from_transactions = sum(t.commission_amount for t in transactions if t.status == 'pending')
        paid_from_transactions = sum(t.commission_amount for t in transactions if t.status == 'paid')
        
        # Calculate ratio to adjust breakdown to match actual affiliate values
        # This ensures breakdown matches the actual pending/paid after cashouts
        if total_from_transactions > 0:
            pending_ratio = pending_earnings / total_earnings if total_earnings > 0 else 0
            paid_ratio = paid_earnings / total_earnings if total_earnings > 0 else 0
        else:
            pending_ratio = 0
            paid_ratio = 0
        
        # Group transactions by period
        period_data = defaultdict(lambda: {
            'totalEarnings': 0.0,
            'pendingEarnings': 0.0,
            'paidEarnings': 0.0,
            'transactionCount': 0,
            'label': ''
        })
        
        for transaction in transactions:
            trans_date = transaction.date
            if not trans_date:
                continue
            
            # Determine period key and label based on period type
            if period == 'daily':
                period_key = trans_date.strftime('%Y-%m-%d')
                period_label = trans_date.strftime('%B %d, %Y')
            elif period == 'weekly':
                # Get the Monday of the week
                monday = trans_date - timedelta(days=trans_date.weekday())
                period_key = monday.strftime('%Y-%m-%d')  # Use Monday date as key
                period_label = f"Week of {monday.strftime('%B %d, %Y')}"
            elif period == 'yearly':
                period_key = trans_date.strftime('%Y')
                period_label = trans_date.strftime('%Y')
            else:  # monthly (default)
                period_key = trans_date.strftime('%Y-%m')
                period_label = trans_date.strftime('%B %Y')
            
            # Add transaction data to period
            period_data[period_key]['totalEarnings'] += transaction.commission_amount
            period_data[period_key]['transactionCount'] += 1
            period_data[period_key]['label'] = period_label
            
            if transaction.status == 'paid':
                period_data[period_key]['paidEarnings'] += transaction.commission_amount
            else:
                period_data[period_key]['pendingEarnings'] += transaction.commission_amount
        
        # Convert to list and sort by period (descending - most recent first)
        breakdown = []
        sorted_periods = sorted(period_data.keys(), reverse=True)[:limit]
        
        for period_key in sorted_periods:
            data = period_data[period_key]
            period_total = data['totalEarnings']
            
            # Adjust pending/paid to match actual affiliate ratios (accounts for cashouts)
            # If we have transactions, distribute based on actual affiliate pending/paid ratios
            if total_earnings > 0 and period_total > 0:
                # Calculate adjusted values based on actual affiliate ratios
                adjusted_pending = period_total * pending_ratio
                adjusted_paid = period_total * paid_ratio
            else:
                # Fallback to transaction-based calculation
                adjusted_pending = data['pendingEarnings']
                adjusted_paid = data['paidEarnings']
            
            breakdown.append({
                'period': period_key,
                'label': data['label'] or period_key,
                'totalEarnings': round(period_total, 2),
                'pendingEarnings': round(adjusted_pending, 2),
                'paidEarnings': round(adjusted_paid, 2),
                'transactionCount': data['transactionCount']
            })
        
        # Calculate total pages (for pagination, though we're limiting results)
        total_items = len(period_data)
        total_pages = 1  # Since we're limiting, we show all in one page
        
        return {
            'summary': {
                'totalEarnings': round(total_earnings, 2),
                'pendingEarnings': round(pending_earnings, 2),
                'paidEarnings': round(paid_earnings, 2),
                'availableBalance': round(pending_earnings, 2),
                # Additional info for clarity
                'totalFromTransactions': round(total_from_transactions, 2),
                'pendingFromTransactions': round(pending_from_transactions, 2),
                'paidFromTransactions': round(paid_from_transactions, 2)
            },
            'breakdown': breakdown,
            'pagination': {
                'currentPage': 1,
                'totalPages': total_pages,
                'totalItems': total_items
            }
        }

