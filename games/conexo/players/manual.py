from games.conexo.common import ConexoFeedback, ConexoInfo
from games.conexo.players.common import ConexoIOPlayer
from players.manual import BaseManualPlayer


class ConexoManualPlayer(
    BaseManualPlayer[ConexoInfo, None, set[int], ConexoFeedback], ConexoIOPlayer
):
    pass
