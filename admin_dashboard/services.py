"""
Admin Dashboard services
"""
from datetime import datetime, timedelta
from admin_dashboard.models import FeeSettings, CashoutRequest, Dispute, ActivityLog
from authentication.models import User, Admin
from products.models import Product, Order, Offer
from affiliates.models import AffiliatePayoutRequest
import random
import string


class DashboardService:
    """Dashboard service"""
    
    @staticmethod
    def get_dashboard_stats():
        """Get dashboard statistics"""
        total_users = User.objects.count()
        active_users = User.objects(status='active').count()
        total_listings = Product.objects.count()
        total_sales = Order.objects(status__in=['ready', 'shipped', 'delivered']).count()
        total_transactions = Order.objects.count()
        
        # Calculate total revenue and fees
        completed_orders = Order.objects(payment_status='completed')
        total_revenue = sum(order.total_price for order in completed_orders)
        total_platform_fees = sum(order.dolabb_fee for order in completed_orders)
        total_affiliate_commissions = sum(order.affiliate_commission for order in completed_orders)
        total_seller_payouts = sum(order.seller_payout for order in completed_orders)
        
        pending_cashouts = CashoutRequest.objects(status='pending').count()
        open_disputes = Dispute.objects(status='open').count()
        resolved_disputes = Dispute.objects(status='resolved').count()
        
        # Get recent activities
        recent_activities = ActivityLog.objects().order_by('-date').limit(10)
        activities_list = [{
            'type': activity.activity_type,
            'details': activity.details,
            'date': activity.date.isoformat()
        } for activity in recent_activities]
        
        return {
            'totalUsers': total_users,
            'activeUsers': active_users,
            'totalListings': total_listings,
            'Total Sales': total_sales,
            'totalTransactions': total_transactions,
            'totalRevenue': total_revenue,
            'totalPlatformFees': total_platform_fees,
            'totalAffiliateCommissions': total_affiliate_commissions,
            'totalSellerPayouts': total_seller_payouts,
            'pendingCashouts': pending_cashouts,
            'recentActivities': activities_list,
            'Open Disputes': open_disputes,
            'resolvedDisputes': resolved_disputes
        }
    
    @staticmethod
    def get_revenue_trends():
        """Get revenue and users trends"""
        # Get monthly revenue for last 12 months
        monthly_revenue = []
        monthly_new_users = []
        
        for i in range(11, -1, -1):
            month_start = datetime.utcnow() - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            
            month_str = month_start.strftime('%Y-%m')
            
            # Revenue for month
            orders = Order.objects(
                created_at__gte=month_start,
                created_at__lt=month_end,
                payment_status='completed'
            )
            revenue = sum(order.total_price for order in orders)
            monthly_revenue.append({'month': month_str, 'revenue': revenue})
            
            # New users for month
            new_users = User.objects(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            monthly_new_users.append({'month': month_str, 'newUsers': new_users})
        
        return {
            'monthlyRevenue': monthly_revenue,
            'monthlyNewUsers': monthly_new_users
        }
    
    @staticmethod
    def get_sales_over_time():
        """Get sales over time"""
        # Daily sales (last 30 days)
        daily_sales = []
        for i in range(29, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            orders = Order.objects(
                created_at__gte=date.replace(hour=0, minute=0, second=0),
                created_at__lt=date.replace(hour=23, minute=59, second=59)
            ).count()
            daily_sales.append({'date': date_str, 'sales': orders})
        
        # Weekly and monthly sales (simplified)
        weekly_sales = []
        monthly_sales = []
        
        for i in range(11, -1, -1):
            week_start = datetime.utcnow() - timedelta(weeks=i)
            week_str = week_start.strftime('%Y-W%U')
            
            orders = Order.objects(
                created_at__gte=week_start,
                created_at__lt=week_start + timedelta(weeks=1)
            ).count()
            weekly_sales.append({'week': week_str, 'sales': orders})
            
            month_start = datetime.utcnow() - timedelta(days=30 * i)
            month_str = month_start.strftime('%Y-%m')
            
            orders = Order.objects(
                created_at__gte=month_start,
                created_at__lt=month_start + timedelta(days=30)
            ).count()
            monthly_sales.append({'month': month_str, 'sales': orders})
        
        return {
            'dailySales': daily_sales,
            'weeklySales': weekly_sales,
            'monthlySales': monthly_sales
        }
    
    @staticmethod
    def get_listings_status_summary():
        """Get listings status summary"""
        return {
            'activeListings': Product.objects(status='active').count(),
            'soldListings': Product.objects(status='sold').count(),
            'removedListings': Product.objects(status='removed').count(),
            'pendingReviewListings': Product.objects(approved=False).count()
        }
    
    @staticmethod
    def get_transaction_types_summary():
        """Get transaction types summary"""
        return {
            'purchaseTransactions': Order.objects().count(),  # All orders
            'offerTransactions': Offer.objects().count(),
            'acceptedOfferTransactions': Offer.objects(status='accepted').count()
        }
    
    @staticmethod
    def get_disputes_status():
        """Get disputes status"""
        return {
            'openDisputes': Dispute.objects(status='open').count(),
            'resolvedDisputes': Dispute.objects(status='resolved').count(),
            'closedDisputes': Dispute.objects(status='closed').count()
        }
    
    @staticmethod
    def get_cashout_requests_summary():
        """Get cashout requests summary"""
        return {
            'pendingCashouts': CashoutRequest.objects(status='pending').count(),
            'approvedCashouts': CashoutRequest.objects(status='approved').count(),
            'rejectedCashouts': CashoutRequest.objects(status='rejected').count()
        }


class UserManagementService:
    """User management service"""
    
    @staticmethod
    def get_users(page=1, limit=20, status_filter=None):
        """Get all users"""
        query = User.objects()
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        total = query.count()
        skip = (page - 1) * limit
        users = query.skip(skip).limit(limit)
        
        users_list = []
        for user in users:
            # Calculate activity
            total_purchases = Order.objects(buyer_id=user.id).count()
            total_spent = sum(order.total_price for order in Order.objects(buyer_id=user.id))
            
            users_list.append({
                '_id': str(user.id),
                'name': user.full_name,
                'email': user.email,
                'type': user.role,
                'status': user.status,
                'joinDate': user.join_date.isoformat(),
                'Activity': {
                    'totalPurchases': total_purchases,
                    'totalSpent': total_spent
                }
            })
        
        return users_list, total
    
    @staticmethod
    def suspend_user(user_id):
        """Suspend user"""
        user = User.objects(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.status = 'suspended'
        user.save()
        
        return user
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate user"""
        user = User.objects(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.status = 'deactivated'
        user.save()
        
        return user
    
    @staticmethod
    def delete_user(user_id):
        """Delete user"""
        user = User.objects(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.delete()
        
        return True


class ListingManagementService:
    """Listing management service"""
    
    @staticmethod
    def get_listings(page=1, limit=20, status_filter=None):
        """Get all listings"""
        query = Product.objects()
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        total = query.count()
        skip = (page - 1) * limit
        listings = query.skip(skip).limit(limit)
        
        listings_list = []
        for listing in listings:
            seller = User.objects(id=listing.seller_id.id).first()
            listings_list.append({
                '_id': str(listing.id),
                'title': listing.title,
                'description': listing.description,
                'sellerId': str(listing.seller_id.id),
                'SellerName': listing.seller_name or (seller.full_name if seller else ''),
                'category': listing.category,
                'price': listing.price,
                'status': listing.status,
                'reviewed': listing.reviewed,
                'approved': listing.approved,
                'createdAt': listing.created_at.isoformat(),
                'images': listing.images
            })
        
        return listings_list, total
    
    @staticmethod
    def approve_listing(listing_id):
        """Approve listing"""
        listing = Product.objects(id=listing_id).first()
        if not listing:
            raise ValueError("Listing not found")
        
        listing.approved = True
        listing.reviewed = True
        listing.save()
        
        return listing
    
    @staticmethod
    def reject_listing(listing_id):
        """Reject listing"""
        listing = Product.objects(id=listing_id).first()
        if not listing:
            raise ValueError("Listing not found")
        
        listing.approved = False
        listing.reviewed = True
        listing.save()
        
        return listing
    
    @staticmethod
    def hide_listing(listing_id):
        """Hide listing"""
        listing = Product.objects(id=listing_id).first()
        if not listing:
            raise ValueError("Listing not found")
        
        listing.status = 'removed'
        listing.save()
        
        return listing


class TransactionService:
    """Transaction service"""
    
    @staticmethod
    def get_transactions(page=1, limit=20, type_filter=None):
        """Get all transactions"""
        query = Order.objects()
        
        if type_filter:
            # Filter by type if needed
            pass
        
        total = query.count()
        skip = (page - 1) * limit
        transactions = query.skip(skip).limit(limit)
        
        transactions_list = []
        for transaction in transactions:
            buyer = User.objects(id=transaction.buyer_id.id).first()
            seller = User.objects(id=transaction.seller_id.id).first()
            product = Product.objects(id=transaction.product_id.id).first()
            
            transactions_list.append({
                '_id': str(transaction.id),
                'type': 'purchase',  # Can be determined from order
                'buyerId': str(transaction.buyer_id.id),
                'buyerName': transaction.buyer_name or (buyer.full_name if buyer else ''),
                'sellerId': str(transaction.seller_id.id),
                'SellerName': transaction.seller_name or (seller.full_name if seller else ''),
                'itemId': str(transaction.product_id.id),
                'itemTitle': transaction.product_title or (product.title if product else ''),
                'offerAmount': transaction.offer_price,
                'originalPrice': transaction.price,
                'dolabbFee': transaction.dolabb_fee,
                'status': transaction.status,
                'date': transaction.created_at.isoformat()
            })
        
        return transactions_list, total


class CashoutService:
    """Cashout service"""
    
    @staticmethod
    def get_cashout_requests(page=1, limit=20, status_filter=None):
        """Get cashout requests"""
        query = CashoutRequest.objects()
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        total = query.count()
        skip = (page - 1) * limit
        requests = query.skip(skip).limit(limit)
        
        requests_list = []
        for req in requests:
            requests_list.append({
                '_id': str(req.id),
                'SellerId': str(req.seller_id.id),
                'SellerName': req.seller_name,
                'amount': req.amount,
                'paymentMethod': req.payment_method if hasattr(req, 'payment_method') else 'Bank Transfer',
                'Requested Date': req.requested_date.isoformat(),
                'Status': req.status,
                'accountDetails': req.account_details,
                'rejectionReason': req.rejection_reason,
                'notes': req.notes if hasattr(req, 'notes') else None
            })
        
        return requests_list, total
    
    @staticmethod
    def approve_cashout(cashout_id, admin_id):
        """Approve cashout request"""
        cashout = CashoutRequest.objects(id=cashout_id).first()
        if not cashout:
            raise ValueError("Cashout request not found")
        
        cashout.status = 'approved'
        cashout.reviewed_at = datetime.utcnow()
        cashout.reviewed_by = admin_id
        cashout.save()
        
        return cashout
    
    @staticmethod
    def reject_cashout(cashout_id, admin_id, reason):
        """Reject cashout request"""
        cashout = CashoutRequest.objects(id=cashout_id).first()
        if not cashout:
            raise ValueError("Cashout request not found")
        
        cashout.status = 'rejected'
        cashout.rejection_reason = reason
        cashout.reviewed_at = datetime.utcnow()
        cashout.reviewed_by = admin_id
        cashout.save()
        
        return cashout


class FeeSettingsService:
    """Fee settings service"""
    
    @staticmethod
    def get_fee_settings():
        """Get fee settings"""
        settings = FeeSettings.objects().first()
        if not settings:
            settings = FeeSettings()
            settings.save()
        
        return {
            'minimumFee': settings.minimum_fee,
            'feePercentage': settings.fee_percentage,
            'thresholdAmount1': settings.threshold_amount_1,
            'thresholdAmount2': settings.threshold_amount_2,
            'maximumFee': settings.maximum_fee,
            'transactionFeeFixed': settings.transaction_fee_fixed,
            'defaultAffiliateCommissionPercentage': settings.default_affiliate_commission_percentage,
            'updatedAt': settings.updated_at.isoformat() if settings.updated_at else None
        }
    
    @staticmethod
    def update_fee_settings(
        minimum_fee=None,
        fee_percentage=None,
        threshold_amount_1=None,
        threshold_amount_2=None,
        maximum_fee=None,
        transaction_fee_fixed=None,
        default_affiliate_commission_percentage=None
    ):
        """Update fee settings"""
        settings = FeeSettings.objects().first()
        if not settings:
            settings = FeeSettings()
        
        if minimum_fee is not None:
            settings.minimum_fee = float(minimum_fee)
        if fee_percentage is not None:
            settings.fee_percentage = float(fee_percentage)
        if threshold_amount_1 is not None:
            settings.threshold_amount_1 = float(threshold_amount_1)
        if threshold_amount_2 is not None:
            settings.threshold_amount_2 = float(threshold_amount_2)
        if maximum_fee is not None:
            settings.maximum_fee = float(maximum_fee)
        if transaction_fee_fixed is not None:
            settings.transaction_fee_fixed = float(transaction_fee_fixed)
        if default_affiliate_commission_percentage is not None:
            settings.default_affiliate_commission_percentage = float(default_affiliate_commission_percentage)
        
        settings.updated_at = datetime.utcnow()
        settings.save()
        
        return settings
    
    @staticmethod
    def get_fee_collection_summary(from_date=None, to_date=None):
        """Get fee collection summary"""
        query = Order.objects(payment_status='completed')
        
        if from_date:
            query = query.filter(created_at__gte=from_date)
        if to_date:
            query = query.filter(created_at__lte=to_date)
        
        total_transactions = query.count()
        total_fees = sum(order.dolabb_fee for order in query)
        avg_fee = total_fees / total_transactions if total_transactions > 0 else 0
        
        return {
            'Total Fees Collected': total_fees,
            'Total Transactions': total_transactions,
            'Time Period': {
                'from': from_date.isoformat() if from_date else None,
                'to': to_date.isoformat() if to_date else None
            },
            'Average Fee per Transaction': avg_fee
        }


class DisputeService:
    """Dispute service"""
    
    @staticmethod
    def generate_case_number():
        """Generate unique case number"""
        year = datetime.utcnow().year
        number = random.randint(1, 9999)
        return f"DISP-{year}-{number:04d}"
    
    @staticmethod
    def create_dispute(buyer_id, order_id, dispute_type, description):
        """Create a dispute/report from buyer"""
        from products.models import Order, Product
        from authentication.models import User
        
        # Verify order exists and belongs to buyer
        order = Order.objects(id=order_id, buyer_id=buyer_id).first()
        if not order:
            raise ValueError("Order not found or does not belong to buyer")
        
        # Get buyer and seller info
        buyer = User.objects(id=buyer_id).first()
        seller = User.objects(id=order.seller_id.id).first()
        product = Product.objects(id=order.product_id.id).first()
        
        if not buyer:
            raise ValueError("Buyer not found")
        
        # Generate case number
        case_number = DisputeService.generate_case_number()
        
        # Ensure case number is unique
        while Dispute.objects(case_number=case_number).first():
            case_number = DisputeService.generate_case_number()
        
        # Create dispute
        dispute = Dispute(
            case_number=case_number,
            dispute_type=dispute_type,
            buyer_id=buyer,
            buyer_name=buyer.full_name or buyer.username,
            seller_id=seller,
            seller_name=order.seller_name or (seller.username if seller else ''),
            item_id=product,
            item_title=order.product_title or (product.title if product else ''),
            description=description,
            status='open'
        )
        dispute.save()
        
        return dispute
    
    @staticmethod
    def get_disputes(page=1, limit=20, status_filter=None):
        """Get disputes"""
        query = Dispute.objects()
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        total = query.count()
        skip = (page - 1) * limit
        disputes = query.skip(skip).limit(limit)
        
        disputes_list = []
        for dispute in disputes:
            disputes_list.append({
                '_id': str(dispute.id),
                'caseNumber': dispute.case_number,
                'type': dispute.dispute_type,
                'buyerId': str(dispute.buyer_id.id),
                'buyerName': dispute.buyer_name,
                'sellerId': str(dispute.seller_id.id),
                'SellerName': dispute.seller_name,
                'itemId': str(dispute.item_id.id),
                'itemTitle': dispute.item_title,
                'description': dispute.description,
                'status': dispute.status,
                'createdAt': dispute.created_at.isoformat(),
                'adminNotes': dispute.admin_notes or '',
                'resolution': dispute.resolution or ''
            })
        
        return disputes_list, total
    
    @staticmethod
    def update_dispute_status(dispute_id, status, admin_notes=None, resolution=None):
        """Update dispute status"""
        dispute = Dispute.objects(id=dispute_id).first()
        if not dispute:
            raise ValueError("Dispute not found")
        
        dispute.status = status
        if admin_notes:
            dispute.admin_notes = admin_notes
        if resolution:
            dispute.resolution = resolution
        
        dispute.updated_at = datetime.utcnow()
        dispute.save()
        
        return dispute
    
    @staticmethod
    def close_dispute(dispute_id, resolution):
        """Close dispute"""
        return DisputeService.update_dispute_status(dispute_id, 'closed', resolution=resolution)

