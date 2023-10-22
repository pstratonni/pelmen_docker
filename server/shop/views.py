from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.permissions import *
from shop.serializers import *
from shop.service import ProductFilter


class ManufacturerAPIList(generics.ListAPIView):
    queryset = Manufacturer.objects.filter(activ=True)
    serializer_class = ManufacturerSerializer


class ManufacturerAPIRetriever(generics.RetrieveAPIView):
    queryset = Manufacturer.objects.filter(activ=True)
    serializer_class = ManufacturerSerializer


class ManufacturerIsAdminAPIList(generics.ListCreateAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = (IsAdminUser,)


class ManufacturerIsAdminAPIRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = (IsAdminUser,)


class ProductAPIListPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 50


class ProductAPIList(generics.ListAPIView):
    queryset = Product.objects.filter(active=True).order_by('-date_created')
    serializer_class = ProductListSerializer
    pagination_class = ProductAPIListPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ('title', 'category__title')
    ordering_fields = ('price',)


class ProductAPIRetriever(generics.RetrieveAPIView):
    queryset = Product.objects.filter(active=True).prefetch_related('composition')
    serializer_class = ProductDetailSerializer


class ProductIsAdminAPIList(generics.ListCreateAPIView):
    queryset = Product.objects.all().prefetch_related('composition')
    serializer_class = ProductListSerializer
    pagination_class = ProductAPIListPagination
    permission_classes = (IsAdminUser,)


class ProductIsAdminAPIRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all().prefetch_related('composition')
    serializer_class = ProductDetailSerializer
    permission_classes = (IsAdminUser,)


class CategoryListView(generics.ListAPIView):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()


class OrderAPIListCreate(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user:
            return Order.objects.filter(user=user)
        return Response([])


class OrderAPIRetrieve(generics.RetrieveAPIView):
    permission_classes = (IsOwnerOrderOrCart,)
    queryset = Order.objects.all().prefetch_related('order_items')
    serializer_class = OrderRetrieveSerializer


class OrderIsAdminAPIList(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-date_created')
    serializer_class = OrderSerializer
    pagination_class = ProductAPIListPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('email', 'id')


class OrderAPIUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAdminUser,)


class OrderItemAPICreate(generics.CreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = (IsOwnerOrderOrCart,)


class OrderItemAPIUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = (IsAdminUser,)


class CartAPIRetrieveUpdateDestroy(APIView):
    permission_classes = (IsOwner,)

    def get(self, request, ):
        cart = Cart.objects.get(user=request.user).prefetch_related('cart_items')
        return Response(CartSerializer(cart).data)


class CartItemAPICreate(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = (IsOwnerOrderOrCart,)


class CartItemAPIDestroy(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = (IsOwnerOrderOrCart,)






