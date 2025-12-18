from games.wordle.common import WordleFeedback, WordleInfo
from games.wordle.players.common import WordleIOPlayer
from players.manual import BaseManualPlayer


class WordleManualPlayer(BaseManualPlayer[WordleInfo, None, str, WordleFeedback], WordleIOPlayer):
    pass
