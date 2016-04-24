# Utility code for messing with SGF files, and converting games to move
# examples.

from gomill import sgf
from gomill import sgf_moves
import h5py
import numpy as np
import zipfile

BOARD_SIZE = 19


def board_to_bitmap(board):
  """Converts a GoMill board object to a 2x19x19 numpy array (two channel
  19x19 bitmap.)  The two channels are (black, white)."""
  black = np.zeros([19, 19], dtype='bool')
  white = np.zeros([19, 19], dtype='bool')
  for color, (row, col) in board.list_occupied_points():
    (black if color == 'b' else white)[(row, col)] = 1

  return np.array([black, white])


def game_to_move_examples(sgf_src):
  """Converts an SGF string to a generator of tuples.

  Each tuple is of the form (board_bitmap, (row, col)) or (board_bitmap,
  None).  We get one such tuple for each move made in the game, where
  board_bitmap is the state of the board before the move is made.

  Here, the board_bitmap's channels are (player_to_move, opponent)
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


def write_np_data(h5_handle, name, np_data):
  dset = h5_handle.create_dataset(
    name, np_data.shape, dtype=np_data.dtype)
  dset[...] = np_data


def save_labelled_examples(examples, h5_output_file):
  """Write the examples (minus moves where the player passes) to an npz
  file.  The file contains three arrays:

  'boards_shape': the shape of the boards array (Nx2x19x19)
  'boards_packed': boards (packed as a 1D bit array.)
  'moves': the moves played (2D array of move coordinates.)
  """

  # For now, throw out passes:

  examples = [e for e in examples if e[1] is not None]

  boards = np.array([example[0] for example in examples], dtype='uint8')

  output_h5 = h5py.File(h5_output_file, 'w')

  boards_shape = np.array(list(boards.shape), dtype='int')
  write_np_data(output_h5, 'boards_shape', boards_shape)

  boards_packed = np.packbits(
    np.array([example[0] for example in examples], dtype='bool'))
  write_np_data(output_h5, 'boards_packed', boards_packed)

  moves = np.array([example[1] for example in examples], dtype='uint8')
  write_np_data(output_h5, 'moves', moves)


def load_labelled_examples(h5_input_file):
  input_h5 = h5py.File(h5_input_file, 'r')
  boards_shape = input_h5['boards_shape']
  boards_size = np.prod(boards_shape)
  boards = np.reshape(np.unpackbits(input_h5['boards_packed'])[:boards_size],
                      boards_shape)
  return zip(list(boards), list(input_h5['moves']))
