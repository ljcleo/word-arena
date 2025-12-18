from games.contexto.common import ContextoFeedback
from games.contexto.players.common import ContextoIOPlayer
from players.manual import BaseManualPlayer


class ContextoManualPlayer(BaseManualPlayer[int, None, str, ContextoFeedback], ContextoIOPlayer):
    pass
