from enum import Enum

import helpers

class CommandType(Enum):
  SET_TRANSACTION = 1
  PART_TRANSACTION = 2
  SEARCH = 3
  NOTE = 4

class Command:
  def __init__(self, text, default_part=None, default_color=None, default_quantity=1):
    if text[0:4] == 'exit':
      exit(0)

    self.type = None
    self.text = text
    self.note = None
    self.set = None
    self.set_num = None
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
        self.set_num, self.set = helpers.search_set(self.set)[0]
        self.type = CommandType.SET_TRANSACTION
      except ValueError:
        if text[0:5] == 'note ':
          self.note = text[5:]
          self.type = CommandType.NOTE
        else:
          self.type = CommandType.SEARCH

    try:
      self.quantity = int(self.quantity)
    except ValueError:
      self.quantity = default_quantity

if __name__ == '__main__':
  last_part = None
  last_color = None
  note = None

  while(True):
    print('')
    if last_part or last_color:
      print('Current part/color: %s %s' % (last_color, last_part))
    if note:
      print('Current Note: %s' % note)
    command = Command(input('> '))

    if command.type == CommandType.NOTE:
      note = command.note
    
    if command.type == CommandType.SEARCH:
      print('Search results:')
      results = helpers.search_part(command.text)[:40]

      try:
        last_part = results[0][1]
      except IndexError:
        pass
      
      for part in results:
        print("{:<10} {}".format(part[0], part[1]))

    if command.type == CommandType.SET_TRANSACTION:
      print("Adding %d %s (%s)" % (command.quantity, command.set, command.set_num))
      helpers.add_set(command.set_num, command.quantity, note)

    if command.type == CommandType.PART_TRANSACTION:
      last_part = command.part
      last_color = command.color
    
      print("Adding %d %s (%d) %s (%s)" % (command.quantity, command.color, command.color_id, command.part, command.part_num))
      helpers.add_part(command.part_num, command.color_id, command.quantity, note)
      