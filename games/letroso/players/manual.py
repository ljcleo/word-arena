from games.letroso.common import LetrosoFeedback, LetrosoInfo
from games.letroso.players.common import LetrosoIOPlayer
from players.manual import BaseManualPlayer


class LetrosoManualPlayer(
    BaseManualPlayer[LetrosoInfo, None, str, LetrosoFeedback], LetrosoIOPlayer
):
    pass
