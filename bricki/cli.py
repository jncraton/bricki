from enum import Enum

import helpers

class CommandType(Enum):
  SET_TRANSACTION = 1
  PART_TRANSACTION = 2

class Command:
  def __init__(self, text):
    if text[0:4] == 'exit':
      exit(0)

    self.type = None
    self.set = None
    self.color = None
    self.part = None
    self.quantity = 0

    try:
      (self.quantity, self.color, self.part) = text.split(',')
      self.type = CommandType.PART_TRANSACTION
    except ValueError:
      try:
        (self.quantity, self.set) = text.split(',')
        self.type = CommandType.SET_TRANSACTION
      except ValueError:
        print('Needs two or three parameters')
        raise ParseError

    self.quantity = int(self.quantity)

if __name__ == '__main__':
  last_part_name = None
  last_color_name = None

  while(True):
    print('\nCurrent part/color: %s %s' % (last_color_name, last_part_name))
    command = Command(input('> '))

    if command.set:
      print("Adding set %d %s" % (command.quantity, command.set))
      continue

    if not command.part:
      command.part = last_part_name

    if not command.color:
      command.color = last_color_name

    color_id, last_color_name = helpers.search_color(command.color)[0]

    part_num, last_part_name = helpers.search_part(command.part)[0]

    print("Adding %d %s %s" % (command.quantity, command.color, command.part))