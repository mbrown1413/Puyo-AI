from puyo.board import PuyoBoard
from puyo.beanfinder import BeanFinder
from puyo.gccontrol import GamecubeControl
from puyo.ai import SimpleComboAI, SimpleGreedyAI

AI_REGISTRY = {
    'simple_combo': SimpleComboAI,
    'simple_greedy': SimpleGreedyAI,
}

DEFAULT_AI_NAME = "simple_combo"
DEFAULT_AI = AI_REGISTRY[DEFAULT_AI_NAME]
