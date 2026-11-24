from typing import List, Dict, Any, Optional
from app.repositories.conversation_repo import conversation_repo, ConversationRepository

class ConversationService:
    def __init__(self, repo: ConversationRepository = conversation_repo):
        self.repo = repo

    def list_conversations(self) -> List[Dict[str, Any]]:
        return self.repo.list_all()

    def create_conversation(self, title: str, provider: str = "llamacpp") -> Dict[str, Any]:
        return self.repo.create(title=title, provider=provider)

    def get_conversation_detail(self, conv_id: str) -> Optional[Dict[str, Any]]:
        conv = self.repo.get_by_id(conv_id)
        if not conv:
            return None
        messages = self.repo.get_messages(conv_id)
        return {
            "conversation": conv,
            "messages": messages
        }

    def append_message(self, conv_id: str, role: str, content: str) -> Optional[Dict[str, Any]]:
        conv = self.repo.get_by_id(conv_id)
        if not conv:
            return None
        return self.repo.add_message(conv_id, role, content)

conversation_service = ConversationService()

