from enum import Enum

import helpers

class CommandType(Enum):
  SET_TRANSACTION = 1
  PART_TRANSACTION = 2

class Command:
  def __init__(self, text, default_part=None, default_color=None, default_quantity=1):
    if text[0:4] == 'exit':
      exit(0)

    self.type = None
    self.set = None
    self.color = None
    self.color_id = None
    self.part = None
    self.part_num = None
    self.quantity = default_quantity

    try:
      (self.quantity, self.color, self.part) = text.split(',')

      if not self.color:
        self.color = default_color
      if not self.part:
        self.part = default_part

      self.color_id, self.color = helpers.search_color(self.color)[0]
      self.part_num, self.part = helpers.search_part(self.part)[0]
                        
      self.type = CommandType.PART_TRANSACTION
    except ValueError:
      try:
        (self.quantity, self.set) = text.split(',')
        self.type = CommandType.SET_TRANSACTION
      except ValueError:
        print('Needs two or three parameters')
        raise ParseError

    try:
      self.quantity = int(self.quantity)
    except ValueError:
      self.quantity = default_quantity

if __name__ == '__main__':
  last_part = None
  last_color = None

  while(True):
    print('\nCurrent part/color: %s %s' % (last_color, last_part))
    command = Command(input('> '))

    if command.type == CommandType.SET_TRANSACTION:
      print("Adding set %d %s" % (command.quantity, command.set))
      continue

    if command.type == CommandType.PART_TRANSACTION:
      last_part = command.part
      last_color = command.color
    
      print("Adding %d %s (%d) %s (%s)" % (command.quantity, command.color, command.color_id, command.part, command.part_num))
      