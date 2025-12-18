from games.contexto.common import ContextoResult
from games.contexto.players.common import ContextoIOPlayer
from players.manual import BaseManualPlayer


class ContextoManualPlayer(BaseManualPlayer[int, None, str, ContextoResult], ContextoIOPlayer):
    pass
