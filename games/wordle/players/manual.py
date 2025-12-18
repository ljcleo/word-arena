from games.wordle.common import WordleInfo, WordleResult
from games.wordle.players.common import WordleIOPlayer
from players.manual import BaseManualPlayer


class WordleManualPlayer(BaseManualPlayer[WordleInfo, None, str, WordleResult], WordleIOPlayer):
    pass
