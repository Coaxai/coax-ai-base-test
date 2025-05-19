from web3 import Web3
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import UserProfile
from django.utils import timezone
from rest_framework.decorators import api_view

# Constants
NFT_CONTRACT_ADDRESS = Web3.to_checksum_address(
    "0xd4e1587e8be83b4d0218c2a79e07362adfc7197f")  # Bera ID Gen1 Contract

# ERC-721 ABI
ERC721_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]


class WalletConnectView(APIView):
    def post(self, request, *args, **kwargs):
        wallet_address = request.data.get('wallet_address')
        if not wallet_address:
            return Response({"error": "wallet_address required"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = UserProfile.objects.get_or_create(
            wallet_address=wallet_address)

        owns_nft = self.check_nft_ownership(wallet_address)

        user.has_nft = owns_nft
        user.save()

        return Response({
            "wallet_address": user.wallet_address,
            "has_nft": user.has_nft,
            "points": user.points,
        })

    def check_nft_ownership(self, wallet_address):
        try:
            web3 = Web3(Web3.HTTPProvider(settings.ARBITRUM_RPC))

            if not web3.is_connected():
                print("Failed to connect to Arbitrum RPC.")
                return False

            contract = web3.eth.contract(
                address=NFT_CONTRACT_ADDRESS, abi=ERC721_ABI)

            balance = contract.functions.balanceOf(
                Web3.to_checksum_address(wallet_address)).call()

            print(f"Balance for {wallet_address}: {balance}")
            return balance > 0

        except Exception as e:
            print(f"Error checking NFT ownership: {e}")
            return False


class GrantAccessView(APIView):
    def post(self, request, *args, **kwargs):
        wallet_address = request.data.get('wallet_address')
        if not wallet_address:
            return Response({"error": "wallet_address is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, created = UserProfile.objects.get_or_create(
                wallet_address=wallet_address)

            # Grant access
            user.grant_access()

            # Award 500 points if they don't already have access active
            if created or not user.points or user.points < 500:
                user.points += 10
                user.save()

            return Response({
                "message": "✅ Access granted successfully. You earned +10 points!",
                "access_expires_at": user.access_expiry_time,
                "current_points": user.points
            })

        except Exception as e:
            print(f"Grant access error: {e}")
            return Response({"error": "Failed to grant access."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckAccessView(APIView):
    def get(self, request, *args, **kwargs):
        wallet_address = request.query_params.get('wallet_address')
        if not wallet_address:
            return Response({"error": "wallet_address is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserProfile.objects.get(wallet_address=wallet_address)
            has_access = user.has_active_access()

            return Response({
                "wallet_address": wallet_address,
                "has_access": has_access,
                "access_expires_at": user.access_expiry_time
            })

        except UserProfile.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def get_user_points(request):
    wallet_address = request.GET.get('wallet_address')
    if not wallet_address:
        return Response({"error": "wallet_address is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = UserProfile.objects.get(wallet_address__iexact=wallet_address)
        return Response({
            "wallet_address": user.wallet_address,
            "points": user.points
        }, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
