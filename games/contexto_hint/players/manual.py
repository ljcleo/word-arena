from games.contexto_hint.players.common import ContextoHintIOPlayer
from players.manual import BaseManualPlayer


class ContextoHintManualPlayer(BaseManualPlayer[None, list[str], int, int], ContextoHintIOPlayer):
    pass
