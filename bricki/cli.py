import helpers

if __name__ == '__main__':
  last_part = None
  last_color = None

  while(True):
    command = input('Enter as quantity, color, part:')
    if command[0:4] == 'exit':
      exit(0)

    try:
      (quantity, color, part) = command.split(',')
    except ValueError:
      print('Needs all three parameters')
      continue

    if not part:
      part = last_part_name

    if not color:
      color = last_color_name

    color, last_color_name = helpers.search_color(color)[0]

    part, last_part_name = helpers.search_part(part)[0]

    print(quantity, color, part)