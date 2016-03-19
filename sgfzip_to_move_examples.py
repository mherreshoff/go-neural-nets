
from gomill import sgf
from gomill import sgf_moves
import numpy as np
import zipfile

BOARD_SIZE = 19


def board_to_bitmap(board):
  """Converts a GoMill board object to a 3x19x19 numpy array (three channel
  19x19 bitmap.)  The three channels are (black, empty, white)."""
  black = np.zeros([19, 19])
  white = np.zeros([19, 19])
  for color, (row, col) in board.list_occupied_points():
    (black if color == 'b' else white)[(row, col)] = 1

  empty = 1 - (black + white)
  return np.array([black, empty, white])


def game_to_move_examples(sgf_src):
  """Converts an SGF string to a generator of tuples.

  Each tuple is of the form (board_bitmap, (row, col)) or (board_bitmap,
  None).  We get one such tuple for each move made in the game, where
  board_bitmap is the state of the board before the move is made.

  Here, the board_bitmap's channels are (player_to_move, empty, opponent)
  """

  sgf_game = sgf.Sgf_game.from_string(sgf_src)

  board, plays = sgf_moves.get_setup_and_moves(sgf_game)

  history = []
  moves = []
  
  for color, move in plays:
    bitmap = board_to_bitmap(board)
    if color == 'w':
      bitmap = np.flipud(bitmap)
    yield (bitmap, move)
    if move is not None:
      row, col = move
      board.play(row, col, color)


def zip_to_sgf_contents(zip_file_name):
  """Converts a path to a zip file to a generator of strings.  The strings are
  the contents of each file in the zipfile whose name end in .sgf."""
  zf = zipfile.ZipFile(zip_file_name, 'r')
  for name in zf.namelist():
    if name.endswith('.sgf'):
      yield zf.read(name)

def sgfzip_to_move_examples(zip_file_name):
  for game in zip_to_sgf_contents(zip_file_name):
    for example in game_to_move_examples(game):
      yield example
