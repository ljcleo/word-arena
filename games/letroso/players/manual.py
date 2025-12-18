from games.letroso.common import LetrosoInfo, LetrosoResult
from games.letroso.players.common import LetrosoIOPlayer
from players.manual import BaseManualPlayer


class LetrosoManualPlayer(BaseManualPlayer[LetrosoInfo, None, str, LetrosoResult], LetrosoIOPlayer):
    pass
