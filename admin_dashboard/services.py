"""
Admin Dashboard services
"""
from datetime import datetime, timedelta
from admin_dashboard.models import FeeSettings, CashoutRequest, Dispute, ActivityLog, HeroSection
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
    def get_recent_activities(limit=10, activity_type=None):
        """Get recent activities"""
        query = ActivityLog.objects()
        
        if activity_type:
            query = query.filter(activity_type=activity_type)
        
        activities = query.order_by('-date').limit(limit)
        
        activities_list = []
        for activity in activities:
            activities_list.append({
                'id': str(activity.id),
                'type': activity.activity_type,
                'details': activity.details,
                'date': activity.date.isoformat()
            })
        
        return activities_list
    
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
        
        # Send policy violation notification
        try:
            from notifications.notification_helper import NotificationHelper
            if user.role == 'seller':
                NotificationHelper.send_policy_violation_warning(str(user.id))
            elif user.role == 'buyer':
                NotificationHelper.send_policy_violation_warning(str(user.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending suspension notification: {str(e)}")
        
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
    
    @staticmethod
    def get_user_details(user_id):
        """Get user details"""
        user = User.objects(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Calculate activity
        orders = Order.objects(buyer_id=user.id)
        total_orders = orders.count()
        total_spent = sum(order.total_price for order in orders)
        
        # Get activity history (recent orders)
        recent_orders = orders.order_by('-created_at').limit(10)
        activity_history = [{
            'action': 'order_placed',
            'date': order.created_at.isoformat(),
            'details': f"Order #{str(order.id)[:8]} - {order.product_title or 'Product'}"
        } for order in recent_orders]
        
        return {
            'id': str(user.id),
            'name': user.full_name,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'status': user.status,
            'profile_image': user.profile_image or '',
            'created_at': user.join_date.isoformat() if hasattr(user, 'join_date') and user.join_date else (user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None),
            'last_login': None,  # Add if available in User model
            'total_orders': total_orders,
            'total_spent': total_spent,
            'account_verified': user.status == 'active',
            'activity_history': activity_history
        }
    
    @staticmethod
    def reactivate_user(user_id, reason=None):
        """Reactivate user"""
        user = User.objects(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if user.status == 'active':
            raise ValueError("User is already active")
        
        user.status = 'active'
        user.save()
        
        return user


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
                'currency': listing.currency or 'SAR',
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
        
        # Send notification to seller
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_listing_published(str(listing.seller_id.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending listing approval notification: {str(e)}")
        
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
    
    @staticmethod
    def update_listing(listing_id, data):
        """Update listing (admin can update any field)"""
        from datetime import datetime
        from products.models import ShippingInfo
        
        listing = Product.objects(id=listing_id).first()
        if not listing:
            raise ValueError("Listing not found")
        
        # Update all fields that are provided
        if 'itemtitle' in data or 'title' in data:
            listing.title = data.get('itemtitle') or data.get('title')
        if 'description' in data:
            listing.description = data['description']
        if 'price' in data:
            listing.price = float(data['price'])
        if 'originalPrice' in data:
            listing.original_price = float(data['originalPrice'])
        if 'category' in data:
            listing.category = data['category']
        if 'subcategory' in data:
            listing.subcategory = data['subcategory']
        if 'brand' in data:
            listing.brand = data['brand']
        if 'currency' in data:
            listing.currency = data['currency']
        if 'Quantity' in data or 'quantity' in data:
            listing.quantity = int(data.get('Quantity') or data.get('quantity', 1))
        if 'Gender' in data or 'gender' in data:
            listing.gender = data.get('Gender') or data.get('gender')
        if 'Size' in data or 'size' in data:
            listing.size = data.get('Size') or data.get('size')
        if 'Color' in data or 'color' in data:
            listing.color = data.get('Color') or data.get('color')
        if 'Condition' in data or 'condition' in data:
            listing.condition = data.get('Condition') or data.get('condition')
        if 'SKU/ID (Optional)' in data or 'sku' in data:
            listing.sku = data.get('SKU/ID (Optional)') or data.get('sku')
        if 'Tags/Keywords' in data or 'tags' in data:
            listing.tags = data.get('Tags/Keywords') or data.get('tags', [])
        if 'Images' in data or 'images' in data:
            # For admin, accept URLs directly (no base64 processing needed)
            listing.images = data.get('Images') or data.get('images', [])
        if 'Shipping Cost' in data or 'shippingCost' in data:
            listing.shipping_cost = float(data.get('Shipping Cost') or data.get('shippingCost', 0.0))
        if 'Processing Time (days)' in data or 'processingTimeDays' in data:
            listing.processing_time_days = int(data.get('Processing Time (days)') or data.get('processingTimeDays', 7))
        if 'status' in data:
            listing.status = data['status']
        if 'approved' in data:
            listing.approved = data['approved']
        if 'reviewed' in data:
            listing.reviewed = data['reviewed']
        if 'Affiliate Code (Optional)' in data or 'affiliateCode' in data:
            affiliate_code = data.get('Affiliate Code (Optional)') or data.get('affiliateCode')
            listing.affiliate_code = affiliate_code if affiliate_code and affiliate_code.strip() else None
        if 'Tax Percentage' in data or 'taxPercentage' in data:
            tax_percentage = data.get('Tax Percentage') or data.get('taxPercentage')
            if tax_percentage is not None:
                try:
                    listing.tax_percentage = float(tax_percentage)
                except (ValueError, TypeError):
                    listing.tax_percentage = None
            else:
                listing.tax_percentage = None
        
        # Update shipping_info if shipping fields are provided
        if 'Shipping Cost' in data or 'Processing Time (days)' in data or 'Shipping Locations' in data:
            if not listing.shipping_info:
                listing.shipping_info = ShippingInfo()
            
            if 'Shipping Cost' in data:
                listing.shipping_info.cost = float(data['Shipping Cost'])
            if 'Processing Time (days)' in data:
                listing.shipping_info.estimated_days = int(data['Processing Time (days)'])
            if 'Shipping Locations' in data:
                listing.shipping_info.locations = data['Shipping Locations']
        
        listing.updated_at = datetime.utcnow()
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
                'currency': product.currency if product else 'SAR',
                'dolabbFee': transaction.dolabb_fee,
                'status': transaction.status,
                'date': transaction.created_at.isoformat()
            })
        
        return transactions_list, total
    
    @staticmethod
    def get_transaction_details(transaction_id):
        """Get transaction details"""
        transaction = Order.objects(id=transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")
        
        buyer = User.objects(id=transaction.buyer_id.id).first()
        seller = User.objects(id=transaction.seller_id.id).first()
        product = Product.objects(id=transaction.product_id.id).first()
        
        # Calculate fees breakdown
        fees_breakdown = {
            'platform_fee': transaction.dolabb_fee or 0.0,
            'payment_processing_fee': 0.0,  # Add if available
            'affiliate_commission': transaction.affiliate_commission or 0.0
        }
        
        return {
            'id': str(transaction.id),
            'order_id': f"ORD-{str(transaction.id)[:8]}",
            'buyer': {
                'id': str(transaction.buyer_id.id),
                'name': transaction.buyer_name or (buyer.full_name if buyer else ''),
                'email': buyer.email if buyer else ''
            },
            'seller': {
                'id': str(transaction.seller_id.id),
                'name': transaction.seller_name or (seller.full_name if seller else ''),
                'email': seller.email if seller else ''
            },
            'item': {
                'id': str(transaction.product_id.id),
                'title': transaction.product_title or (product.title if product else ''),
                'price': transaction.price or 0.0
            },
            'currency': product.currency if product else 'SAR',
            'amount': transaction.total_price or 0.0,
            'shipping_cost': transaction.shipping_cost or 0.0,
            'platform_fee': transaction.dolabb_fee or 0.0,
            'seller_payout': transaction.seller_payout or 0.0,
            'status': transaction.status,
            'payment_method': 'credit_card',  # Add if available in Order model
            'created_at': transaction.created_at.isoformat(),
            'completed_at': transaction.updated_at.isoformat() if transaction.status == 'delivered' else None,
            'fees_breakdown': fees_breakdown
        }


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
        
        # Send notification to seller
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_payout_sent(str(cashout.seller_id.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending payout notification: {str(e)}")
        
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
        
        # Send notification to seller
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_payout_failed(str(cashout.seller_id.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending payout failed notification: {str(e)}")
        
        return cashout
    
    @staticmethod
    def get_cashout_details(cashout_id):
        """Get cashout request details"""
        cashout = CashoutRequest.objects(id=cashout_id).first()
        if not cashout:
            raise ValueError("Cashout request not found")
        
        seller = User.objects(id=cashout.seller_id.id).first()
        
        # Get transaction history for this seller
        orders = Order.objects(seller_id=cashout.seller_id.id, payment_status='completed').order_by('-created_at').limit(10)
        transaction_history = [{
            'order_id': f"ORD-{str(order.id)[:8]}",
            'amount': order.seller_payout or 0.0,
            'date': order.created_at.isoformat()
        } for order in orders]
        
        return {
            'id': str(cashout.id),
            'seller': {
                'id': str(cashout.seller_id.id),
                'name': cashout.seller_name or (seller.full_name if seller else ''),
                'email': seller.email if seller else ''
            },
            'amount': cashout.amount,
            'status': cashout.status,
            'payment_method': cashout.payment_method if hasattr(cashout, 'payment_method') else 'Bank Transfer',
            'account_details': {
                'account_details': cashout.account_details or '',
                'bank_name': '',  # Add if available
                'account_number': '',  # Add if available
                'routing_number': ''  # Add if available
            },
            'requested_at': cashout.requested_date.isoformat(),
            'processed_at': cashout.reviewed_at.isoformat() if cashout.reviewed_at else None,
            'processed_by': cashout.reviewed_by or None,
            'rejection_reason': cashout.rejection_reason or None,
            'transaction_history': transaction_history
        }


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
    
    @staticmethod
    def calculate_fee(amount):
        """Calculate fee for a given transaction amount"""
        settings = FeeSettings.objects().first()
        if not settings:
            settings = FeeSettings()
            settings.save()
        
        # Calculate fee based on settings
        base_fee = float(amount) * (settings.fee_percentage / 100.0)
        
        # Apply minimum and maximum
        if base_fee < settings.minimum_fee:
            base_fee = settings.minimum_fee
        elif base_fee > settings.maximum_fee:
            base_fee = settings.maximum_fee
        
        total_fee = base_fee + settings.transaction_fee_fixed
        
        return {
            'transaction_amount': float(amount),
            'platform_fee': total_fee,
            'fee_percentage': settings.fee_percentage,
            'minimum_fee': settings.minimum_fee,
            'maximum_fee': settings.maximum_fee,
            'fee_breakdown': {
                'base_fee': base_fee,
                'transaction_fee_fixed': settings.transaction_fee_fixed,
                'total_fee': total_fee
            },
            'seller_payout': float(amount) - total_fee,
            'net_amount': float(amount) - total_fee
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
            order_id=order,
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
        from products.models import Order
        
        query = Dispute.objects()
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        total = query.count()
        skip = (page - 1) * limit
        disputes = query.skip(skip).limit(limit)
        
        disputes_list = []
        for dispute in disputes:
            # Get order to fetch order_number - handle broken references safely
            order = None
            order_id = ''
            order_number = ''
            if dispute.order_id:
                try:
                    order_obj_id = dispute.order_id.id if hasattr(dispute.order_id, 'id') else dispute.order_id
                    order = Order.objects(id=order_obj_id).first()
                    if order:
                        order_id = str(order.id)
                        order_number = order.order_number if hasattr(order, 'order_number') else ''
                except (AttributeError, Exception):
                    # Order reference is broken or order doesn't exist
                    order_id = ''
                    order_number = ''
            
            disputes_list.append({
                '_id': str(dispute.id),
                'caseNumber': dispute.case_number,
                'type': dispute.dispute_type,
                'buyerId': str(dispute.buyer_id.id),
                'buyerName': dispute.buyer_name,
                'sellerId': str(dispute.seller_id.id),
                'SellerName': dispute.seller_name,
                'orderId': order_id,
                'orderNumber': order_number,
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
        
        # Send notifications if dispute is resolved
        if status == 'resolved':
            try:
                from notifications.notification_helper import NotificationHelper
                # Notify seller
                NotificationHelper.send_dispute_resolved(str(dispute.seller_id.id), 'seller')
                # Notify buyer
                NotificationHelper.send_dispute_resolved(str(dispute.buyer_id.id), 'buyer')
            except Exception as e:
                import logging
                logging.error(f"Error sending dispute resolution notifications: {str(e)}")
        
        return dispute
    
    @staticmethod
    def close_dispute(dispute_id, resolution):
        """Close dispute"""
        return DisputeService.update_dispute_status(dispute_id, 'closed', resolution=resolution)
    
    @staticmethod
    def get_buyer_disputes(buyer_id, page=1, limit=20, status_filter=None):
        """Get disputes for a specific buyer"""
        from products.models import Order
        
        query = Dispute.objects(buyer_id=buyer_id)
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        total = query.count()
        skip = (page - 1) * limit
        disputes = query.order_by('-created_at').skip(skip).limit(limit)
        
        disputes_list = []
        for dispute in disputes:
            # Get order to fetch order_number - handle broken references safely
            order = None
            order_id = ''
            order_number = ''
            if dispute.order_id:
                try:
                    order_obj_id = dispute.order_id.id if hasattr(dispute.order_id, 'id') else dispute.order_id
                    order = Order.objects(id=order_obj_id).first()
                    if order:
                        order_id = str(order.id)
                        order_number = order.order_number if hasattr(order, 'order_number') else ''
                except (AttributeError, Exception):
                    # Order reference is broken or order doesn't exist
                    order_id = ''
                    order_number = ''
            
            disputes_list.append({
                '_id': str(dispute.id),
                'caseNumber': dispute.case_number,
                'type': dispute.dispute_type,
                'buyerName': dispute.buyer_name,
                'sellerName': dispute.seller_name,
                'orderId': order_id,
                'orderNumber': order_number,
                'itemTitle': dispute.item_title,
                'description': dispute.description,
                'status': dispute.status,
                'createdAt': dispute.created_at.isoformat(),
                'updatedAt': dispute.updated_at.isoformat(),
                'messageCount': len(dispute.messages) if dispute.messages else 0
            })
        
        return disputes_list, total
    
    @staticmethod
    def get_dispute_details(dispute_id, user_id=None, user_type=None):
        """Get dispute details"""
        dispute = Dispute.objects(id=dispute_id).first()
        if not dispute:
            raise ValueError("Dispute not found")
        
        # Check if user has access (buyer can only see their own disputes)
        if user_id and user_type == 'buyer':
            if str(dispute.buyer_id.id) != user_id:
                raise ValueError("Unauthorized: You can only view your own disputes")
        
        buyer = User.objects(id=dispute.buyer_id.id).first()
        seller = User.objects(id=dispute.seller_id.id).first()
        product = Product.objects(id=dispute.item_id.id).first()
        
        # Safely get order information - handle cases where order_id is None or order doesn't exist
        order = None
        order_id = ''
        order_number = ''
        if dispute.order_id:
            try:
                # Try to get the order - handle both ReferenceField and direct ID access
                order_obj_id = dispute.order_id.id if hasattr(dispute.order_id, 'id') else dispute.order_id
                order = Order.objects(id=order_obj_id).first()
                if order:
                    order_id = str(order.id)
                    order_number = order.order_number if hasattr(order, 'order_number') else ''
                else:
                    # Order reference exists but order not found in database
                    import logging
                    logging.warning(f"Dispute {dispute_id} has order_id reference but order {order_obj_id} not found in database")
            except (AttributeError, Exception) as e:
                # Order reference is broken or order doesn't exist
                import logging
                logging.warning(f"Error fetching order for dispute {dispute_id}: {str(e)}")
                order = None
                order_id = ''
                order_number = ''
        
        # Format messages (includes both buyer and admin comments)
        messages = []
        if dispute.messages:
            # Sort messages by creation date to ensure chronological order
            sorted_messages = sorted(dispute.messages, key=lambda x: x.created_at)
            for msg in sorted_messages:
                message_data = {
                    'message': msg.message,
                    'senderType': msg.sender_type,
                    'senderId': msg.sender_id,
                    'senderName': msg.sender_name,
                    'createdAt': msg.created_at.isoformat()
                }
                # Include order information for all messages when viewed by admin
                if not user_type or user_type != 'buyer':  # Admin view
                    message_data['orderId'] = order_id
                    message_data['orderNumber'] = order_number
                messages.append(message_data)
        
        # Build timeline
        timeline = [
            {
                'action': 'dispute_created',
                'date': dispute.created_at.isoformat(),
                'by': 'buyer'
            }
        ]
        if dispute.updated_at and dispute.updated_at != dispute.created_at:
            timeline.append({
                'action': 'dispute_updated',
                'date': dispute.updated_at.isoformat(),
                'by': 'admin'
            })
        
        return {
            'id': str(dispute.id),
            'caseNumber': dispute.case_number,
            'type': dispute.dispute_type,
            'buyer': {
                'id': str(dispute.buyer_id.id),
                'name': dispute.buyer_name,
                'email': buyer.email if buyer else ''
            },
            'seller': {
                'id': str(dispute.seller_id.id),
                'name': dispute.seller_name,
                'email': seller.email if seller else ''
            },
            'order': {
                'id': order_id,
                'orderNumber': order_number
            },
            'item': {
                'id': str(dispute.item_id.id),
                'title': dispute.item_title,
                'price': product.price if product else 0.0
            },
            'description': dispute.description,
            'status': dispute.status,
            'adminNotes': dispute.admin_notes or '',
            'resolution': dispute.resolution or '',
            'created_at': dispute.created_at.isoformat(),
            'updated_at': dispute.updated_at.isoformat(),
            'messages': messages,
            'timeline': timeline
        }
    
    @staticmethod
    def add_dispute_comment(dispute_id, message, sender_id, sender_type, sender_name):
        """Add comment to dispute (buyer or admin)"""
        from admin_dashboard.models import DisputeMessage
        
        dispute = Dispute.objects(id=dispute_id).first()
        if not dispute:
            raise ValueError("Dispute not found")
        
        if sender_type not in ['buyer', 'admin']:
            raise ValueError("Invalid sender type. Must be 'buyer' or 'admin'")
        
        # Verify buyer can only comment on their own disputes
        if sender_type == 'buyer' and str(dispute.buyer_id.id) != sender_id:
            raise ValueError("Unauthorized: You can only comment on your own disputes")
        
        # Create message
        dispute_message = DisputeMessage(
            message=message,
            sender_type=sender_type,
            sender_id=sender_id,
            sender_name=sender_name,
            created_at=datetime.utcnow()
        )
        
        # Add to dispute messages
        if not dispute.messages:
            dispute.messages = []
        dispute.messages.append(dispute_message)
        dispute.updated_at = datetime.utcnow()
        dispute.save()
        
        # Send email notification if admin replied
        if sender_type == 'admin':
            try:
                buyer = User.objects(id=dispute.buyer_id.id).first()
                if buyer and buyer.email:
                    from notifications.email_templates import send_notification_email
                    from notifications.templates import get_notification_template
                    
                    # Get user language preference (default to 'en')
                    user_language = getattr(buyer, 'language', 'en') or 'en'
                    if user_language not in ['en', 'ar']:
                        user_language = 'en'
                    
                    # Create custom notification for admin reply
                    if user_language == 'ar':
                        email_title = f'رد جديد على النزاع {dispute.case_number}'
                        email_message = f'قام المسؤول بالرد على نزاعك. يرجى تسجيل الدخول لعرض الرد.'
                    else:
                        email_title = f'New Reply on Dispute {dispute.case_number}'
                        email_message = f'An admin has replied to your dispute. Please log in to view the response.'
                    
                    # Get buyer name for personalization
                    buyer_name = dispute.buyer_name or (buyer.username if buyer else 'User')
                    
                    send_notification_email(
                        email=buyer.email,
                        notification_title=email_title,
                        notification_message=email_message,
                        notification_type='info',
                        user_name=buyer_name,
                        language=user_language
                    )
            except Exception as e:
                import logging
                logging.error(f"Error sending dispute reply email notification: {str(e)}")
        
        # Get order information if available (especially for admin comments)
        # Handle cases where order_id is None, broken reference, or order doesn't exist
        order_id = ''
        order_number = ''
        if dispute.order_id:
            try:
                from products.models import Order
                # Try to get the order - handle both ReferenceField and direct ID access
                order_obj_id = dispute.order_id.id if hasattr(dispute.order_id, 'id') else dispute.order_id
                order = Order.objects(id=order_obj_id).first()
                if order:
                    order_id = str(order.id)
                    order_number = order.order_number if hasattr(order, 'order_number') else ''
                else:
                    # Order reference exists but order not found in database
                    import logging
                    logging.warning(f"Dispute {dispute_id} has order_id reference but order {order_obj_id} not found when adding comment")
            except (AttributeError, Exception) as e:
                # Order reference is broken or order doesn't exist - use empty values
                import logging
                logging.warning(f"Error fetching order for dispute {dispute_id} when adding comment: {str(e)}")
                order_id = ''
                order_number = ''
        
        comment_response = {
            'id': str(dispute_message.id) if hasattr(dispute_message, 'id') else 'temp_id',
            'message': dispute_message.message,
            'senderType': dispute_message.sender_type,
            'senderId': dispute_message.sender_id,
            'senderName': dispute_message.sender_name,
            'createdAt': dispute_message.created_at.isoformat()
        }
        
        # Include order information for admin comments
        if sender_type == 'admin':
            comment_response['orderId'] = order_id
            comment_response['orderNumber'] = order_number
        
        return comment_response
    
    @staticmethod
    def add_dispute_message(dispute_id, message, message_type, admin_id):
        """Add admin note/message to dispute (legacy method for backward compatibility)"""
        from authentication.models import User
        admin = User.objects(id=admin_id).first()
        admin_name = admin.full_name or admin.username if admin else 'Admin'
        
        return DisputeService.add_dispute_comment(
            dispute_id=dispute_id,
            message=message,
            sender_id=admin_id,
            sender_type='admin',
            sender_name=admin_name
        )


class HeroSectionService:
    """Hero section service"""
    
    @staticmethod
    def get_hero_section(active_only=False):
        """Get hero section"""
        if active_only:
            hero = HeroSection.objects(is_active=True).first()
        else:
            hero = HeroSection.objects().first()
        
        if not hero:
            # Return default values if no hero section exists
            return {
                'id': None,
                'backgroundType': 'image',
                'imageUrl': '',
                'singleColor': '#4F46E5',
                'gradientColors': ['#667eea', '#764ba2'],
                'gradientDirection': 'to right',
                'title': 'Welcome to Dolabb',
                'subtitle': 'Your marketplace for amazing products',
                'buttonText': 'Get Started',
                'buttonLink': '/products',
                'textColor': '#FFFFFF',
                'isActive': False,
                'createdAt': None,
                'updatedAt': None
            }
        
        return {
            'id': str(hero.id),
            'backgroundType': hero.background_type,
            'imageUrl': hero.image_url or '',
            'singleColor': hero.single_color or '#4F46E5',
            'gradientColors': hero.gradient_colors or ['#667eea', '#764ba2'],
            'gradientDirection': hero.gradient_direction or 'to right',
            'title': hero.title,
            'subtitle': hero.subtitle or '',
            'buttonText': hero.button_text or '',
            'buttonLink': hero.button_link or '',
            'textColor': hero.text_color or '#FFFFFF',
            'isActive': hero.is_active,
            'createdAt': hero.created_at.isoformat() if hero.created_at else None,
            'updatedAt': hero.updated_at.isoformat() if hero.updated_at else None
        }
    
    @staticmethod
    def update_hero_section(data):
        """Update hero section"""
        hero = HeroSection.objects().first()
        
        if not hero:
            hero = HeroSection()
        
        # Update background settings
        if 'backgroundType' in data:
            background_type = data['backgroundType']
            # Handle if it comes as a list (from FormData)
            if isinstance(background_type, list):
                background_type = background_type[0] if background_type else None
            # Normalize: strip whitespace and convert to lowercase
            if background_type:
                background_type = str(background_type).strip().lower()
            # Map common variations to valid values
            type_mapping = {
                'singlecolor': 'single_color',
                'single-color': 'single_color',
                'single color': 'single_color',
                'gradient': 'gradient',
                'image': 'image',
                'img': 'image'
            }
            background_type = type_mapping.get(background_type, background_type)
            
            if background_type not in ['image', 'single_color', 'gradient']:
                raise ValueError(f"Invalid background type: '{data.get('backgroundType')}' (normalized: '{background_type}'). Must be 'image', 'single_color', or 'gradient'")
            hero.background_type = background_type
        
        if 'imageUrl' in data:
            hero.image_url = data['imageUrl']
        
        if 'singleColor' in data:
            # Validate hex color format
            color = data['singleColor']
            if color and not color.startswith('#'):
                raise ValueError("Color must be in hex format (e.g., '#FF5733')")
            hero.single_color = color
        
        if 'gradientColors' in data:
            colors = data['gradientColors']
            # Handle if it comes as JSON string
            if isinstance(colors, str):
                try:
                    import json
                    colors = json.loads(colors)
                except:
                    # If not JSON, try splitting by comma
                    colors = [c.strip() for c in colors.split(',') if c.strip()]
            # Handle if it comes as a list with single JSON string
            elif isinstance(colors, list) and len(colors) == 1 and isinstance(colors[0], str):
                try:
                    import json
                    colors = json.loads(colors[0])
                except:
                    colors = colors
            if colors:
                # Validate all colors are hex format
                for color in colors:
                    if color and not str(color).startswith('#'):
                        raise ValueError(f"Gradient color '{color}' must be in hex format (e.g., '#FF5733')")
            hero.gradient_colors = colors if colors else []
        
        if 'gradientDirection' in data:
            hero.gradient_direction = data['gradientDirection']
        
        # Update text content
        if 'title' in data:
            hero.title = data['title']
        
        if 'subtitle' in data:
            hero.subtitle = data.get('subtitle', '')
        
        if 'buttonText' in data:
            hero.button_text = data.get('buttonText', '')
        
        if 'buttonLink' in data:
            hero.button_link = data.get('buttonLink', '')
        
        # Update text color
        if 'textColor' in data:
            color = data['textColor']
            if color and not color.startswith('#'):
                raise ValueError("Text color must be in hex format (e.g., '#FFFFFF')")
            hero.text_color = color
        
        # Update status
        if 'isActive' in data:
            hero.is_active = bool(data['isActive'])
        
        hero.updated_at = datetime.utcnow()
        hero.save()
        
        return HeroSectionService.get_hero_section()

