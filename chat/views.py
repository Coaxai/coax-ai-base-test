import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from users.models import UserProfile
from chat.models import ChatSession, ChatMessage, PrizeConfig, Winner

TOGETHER_API_KEY = "281f21cb89d9d80400b50a4628db0c47e2135866d51a6a7e5b123059badb3087"

BASE_PROJECT_CONTEXT = (
    "You are CoaxAI, a savage but funny chatbot.\n"
    "You are part of the CoaxAI project building on the Bera blockchain (currently Testnet).\n"
    "Your job is to roast users, make fun of them playfully, and engage them.\n"
    "You must also answer questions about CoaxAI, Bera chain, and user points clearly.\n"
    "If asked about points, check user's total points and respond."
)

BASE_SAVAGE_PROMPT = (
    "You are CoaxAI, savage but short and witty.\n"
    "- Roast users in 1-2 sentences.\n"
    "- Use normal sentence casing.\n"
    "- Short, smart insults.\n"
    "- Laugh harder if they mention prizes.\n"
)

BASE_WINNER_PROMPT = (
    "You are CoaxAI, now friendly and celebratory.\n"
    "- Congratulate the user nicely.\n"
    "- Confirm they have won the prize.\n"
    "- Tell them their prize will be sent within 24 hours.\n"
    "- Tell them they also earned +200 bonus points for winning."
)

BASE_ALREADY_WON_PROMPT = (
    "You are CoaxAI, polite and informative.\n"
    "- Tell the user they have already won.\n"
)

BASE_PRIZE_OVER_PROMPT = (
    "You are CoaxAI, factual and short.\n"
    "- Inform users that the prizes have been claimed.\n"
)

class ChatAPIView(APIView):
    def post(self, request, *args, **kwargs):
        wallet_address = request.data.get('wallet_address')
        user_message = request.data.get('message')

        if not wallet_address or not user_message:
            return Response({"error": "Missing wallet address or message."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserProfile.objects.get(wallet_address__iexact=wallet_address)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if not user.has_active_access():
            return Response({"error": "Access expired."}, status=status.HTTP_403_FORBIDDEN)

        session, _ = ChatSession.objects.get_or_create(
            user=user,
            active=True,
            defaults={'expires_at': timezone.now() + timedelta(hours=24)}
        )

        # Check cooldown
        last_message = ChatMessage.objects.filter(session=session, sender="user").order_by('-created_at').first()
        if last_message and (timezone.now() - last_message.created_at).total_seconds() < 10:
            wait_seconds = 10 - int((timezone.now() - last_message.created_at).total_seconds())
            return Response({"error": f"Please wait {wait_seconds}s before sending another message.", "cooldown": wait_seconds}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            # Save user message and give 20 points
            ChatMessage.objects.create(session=session, sender="user", content=user_message)
            user.points += 20
            user.save()

            prize = PrizeConfig.objects.filter(active=True).first()
            already_won = Winner.objects.filter(user=user).exists()
            total_winners = Winner.objects.count()
            triggered = False

            if prize and not already_won and total_winners < 5:
                trigger_phrases = [phrase.strip().lower() for phrase in prize.trigger_phrases.split(",")]
                user_message_lower = user_message.lower()
                for phrase in trigger_phrases:
                    if phrase and phrase in user_message_lower:
                        triggered = True
                        break

            if triggered:
                Winner.objects.create(user=user, prize=prize)
                user.points += 200  # +200 bonus points
                user.save()

            # Build memory
            history = ChatMessage.objects.filter(session=session).order_by('created_at')[:10]
            memory_snippets = ""
            for msg in history:
                if msg.sender == "user":
                    memory_snippets += f"- User said: \"{msg.content}\"\n"
                else:
                    memory_snippets += f"- CoaxAI replied: \"{msg.content}\"\n"

            # Detect name
            known_name = None
            for msg in history:
                if "my name is" in msg.content.lower():
                    known_name = msg.content.split("is")[-1].strip().split()[0]
                    break

            # Select system prompt
            if already_won:
                system_prompt = BASE_ALREADY_WON_PROMPT
            elif prize and total_winners >= 5:
                system_prompt = BASE_PRIZE_OVER_PROMPT
            elif triggered:
                system_prompt = BASE_WINNER_PROMPT
            else:
                system_prompt = BASE_SAVAGE_PROMPT
                if prize:
                    system_prompt += f"\n\nPrize: {prize.prize_name} ({prize.prize_amount} BERA)."

            full_system_prompt = BASE_PROJECT_CONTEXT + "\n\n" + system_prompt
            full_system_prompt += f"\n\nUser has {user.points} points now.\n"
            full_system_prompt += "\nMemory of conversation:\n" + memory_snippets
            if known_name:
                full_system_prompt += f"\n\nRemember, user said their name is {known_name}."

            conversation = [
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_message}
            ]

            together_url = "https://api.together.xyz/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "meta-llama/Llama-3-8b-chat-hf",
                "messages": conversation,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 400,
            }

            response = requests.post(together_url, headers=headers, json=payload)

            if response.status_code == 429:
                return Response({"error": "Rate limit hit."}, status=429)

            response.raise_for_status()
            data = response.json()

            ai_response = data['choices'][0]['message']['content'].strip()

            if not ai_response:
                ai_response = "😂 CoaxAI refuses to waste effort today."

            ChatMessage.objects.create(session=session, sender="ai", content=ai_response)

            return Response({"ai_response": ai_response})

        except requests.exceptions.RequestException as e:
            print("❌ Together AI Error:", str(e))
            return Response({"error": "Failed to talk to Together AI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatHistoryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        wallet_address = request.GET.get("wallet_address")

        if not wallet_address:
            return Response({"error": "Missing wallet address."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserProfile.objects.get(wallet_address__iexact=wallet_address)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        session = ChatSession.objects.filter(user=user, active=True).first()
        if not session:
            return Response({"messages": []})

        messages = ChatMessage.objects.filter(session=session).order_by("created_at")
        serialized = [
            {
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            } for msg in messages
        ]

        return Response({"messages": serialized}, status=status.HTTP_200_OK)