from django.db.models import Q, F
from django.shortcuts import render
from icecream import ic
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from purchaser.models import Purchaser
from purchaser.serializer import PurchaserRetrieveSerializer, PurchaserListSerializer
from shop.permissions import IsOwner


class PurchaserAPIRetrieve(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PurchaserRetrieveSerializer
    permission_classes = (IsOwner,)
    queryset = Purchaser.objects.annotate(orders=F('user__orders')).prefetch_related('favorite_product')



class PurchaserAPIList(generics.ListAPIView):
    queryset = Purchaser.objects.all().prefetch_related('favorite_product')
    serializer_class = PurchaserListSerializer
    permission_classes = (IsAdminUser,)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
        })
