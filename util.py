# Utility code for messing with SGF files, and converting games to move
# examples.

from gomill import sgf
from gomill import sgf_moves
import h5py
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

def save_labelled_examples(examples, h5_output_file):
  """Write the examples (minus moves where the player passes) to an npz
  file.  The file contains two arrays.  Boards Nx3x19x19 and labels (the
  moves) Nx2."""

  # For now, throw out passes:
  examples = [e for e in examples if e[1] is not None]

  output_h5 = h5py.File(h5_output_file, 'w')

  boards = np.array([example[0] for example in examples], dtype='float32')
  boards_dset = output_h5.create_dataset(
    'boards', boards.shape, dtype='float32')
  boards_dset[...] = boards

  moves = np.array([example[1] for example in examples], dtype='float32')
  moves_dset = output_h5.create_dataset(
    'moves', moves.shape, dtype='float32')
  moves_dset[...] = moves


def load_labelled_examples(h5_input_file):
  input_h5 = h5py.File(h5_input_file, 'r')
  return zip(list(input_h5['boards']), list(input_h5['moves']))


