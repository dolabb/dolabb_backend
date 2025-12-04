"""
Category views for public category API endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from products.services import ProductService


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_categories(request):
    """
    Get all categories with their subcategories and featured collections.
    
    Endpoint: GET /api/categories/
    Authentication: Not required (public endpoint)
    """
    try:
        categories = ProductService.get_all_categories_formatted()
        
        return Response({
            'success': True,
            'categories': categories
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e),
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_details(request, category_key):
    """
    Get detailed information about a specific category.
    
    Endpoint: GET /api/categories/{category_key}/
    Authentication: Not required
    Parameters:
        category_key (path): The category key (e.g., women, men, watches, jewellery, accessories)
    """
    try:
        category = ProductService.get_category_details(category_key)
        
        return Response({
            'success': True,
            'category': category
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_CATEGORY',
                'message': str(e),
                'details': {}
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e),
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_filters(request, category_key):
    """
    Get available filter options for a specific category/subcategory.
    
    Endpoint: GET /api/categories/{category_key}/filters/
    Authentication: Not required
    Query Parameters:
        subcategory (optional): Filter by subcategory to get relevant options
    """
    try:
        subcategory = request.GET.get('subcategory', '').strip()
        subcategory = subcategory if subcategory else None
        
        filters = ProductService.get_category_filters(category_key, subcategory)
        
        return Response({
            'success': True,
            'filters': filters
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_CATEGORY',
                'message': str(e),
                'details': {}
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e),
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

