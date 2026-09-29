from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .agent import run_agent


class ChatView(APIView):
    """
    FR-24/NFR-02: AI Assistant chat endpoint - authenticated users only.

    Request body:
      {"message": "...", "conversation": [...]}            -- normal turn
      {"conversation": [...], "confirm": true}              -- user approved
                                                                 a pending
                                                                 critical action

    `conversation` is whatever this endpoint returned last time in
    `conversation` - the client just carries it forward unchanged.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        message = request.data.get("message", "")
        conversation = request.data.get("conversation") or []
        confirm = bool(request.data.get("confirm", False))

        if not confirm and not message:
            return Response(
                {"detail": "message is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        result = run_agent(request.user, message, conversation=conversation, confirm=confirm)
        return Response(result)
