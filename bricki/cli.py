from enum import Enum
import subprocess

import helpers

help = """
Commands:
  {quantity},{color},{part} - inserts a part transaction
  {quantity},{color} - inserts a part transaction using the most recent part
  {quantity},{set} - insterts a set transaction
  0,{color},{part} - gets current part count
  .note {str} - sets the note to use for future transactions
  .recent - lists recent transactions
  .undo - remvoes last transaction
  .rb - show current part on Rebrickable
  .help - show this message
  .exit - exits the program
  {anything else} - search
"""


class CommandType(Enum):
    SET_TRANSACTION = 1
    PART_TRANSACTION = 2
    SEARCH = 3
    NOTE = 4
    RECENT = 5
    UNDO = 6
    SHOW_REBRICKABLE = 7


class Command:
    """
    Parses a single command

    >>> Command('.note my_note').type.name
    'NOTE'
    >>> Command('.note my_note').note
    'my_note'
    >>> Command('.recent').type.name
    'RECENT'
    >>> Command('Brick 1x4').type.name
    'SEARCH'
    >>> Command('61,red,Brick 1x4').type.name
    'PART_TRANSACTION'
    >>> Command('61,red,Brick 1x4').part
    'Brick 1 x 4'
    >>> Command('6,red,Brick 1x4').color
    'Red'
    >>> Command('6,red,Brick 1x4').quantity
    6
    """

    def __init__(self, text, default_part=None, default_color=None, default_quantity=1):
        self.type = None
        self.text = text
        self.note = None
        self.set = None
        self.set_num = None
        self.color = default_color
        self.color_id = None
        self.part = default_part
        self.part_num = None
        self.quantity = default_quantity

        try:
            (self.quantity, self.color, self.part) = text.split(",")

            if not self.color:
                self.color = default_color
            if not self.part:
                self.part = default_part

            try:
                self.color_id, self.color = helpers.search_color(self.color)[0]
            except IndexError:
                print("Color not found: %s" % self.color)
                self.type = None
                return
            try:
                self.part_num, self.part = helpers.search_part(self.part)[0]
            except IndexError:
                print("Part not found: %s" % self.part)
                self.type = None
                return

            self.type = CommandType.PART_TRANSACTION
        except ValueError:
            try:
                (self.quantity, self.color) = text.split(",")
                if not self.color:
                    self.color = default_color
                try:
                    self.color_id, self.color = helpers.search_color(self.color)[0]
                    self.part_num, self.part = helpers.search_part(self.part)[0]

                    self.type = CommandType.PART_TRANSACTION
                except IndexError:
                    try:
                        self.set_num, self.set = helpers.search_set(self.color)[0]
                        self.type = CommandType.SET_TRANSACTION
                    except IndexError:
                        print("Color not found: %s" % self.color)
                        self.type = None
                        return
            except ValueError:
                if text == ".exit":
                    exit(0)
                elif text == ".recent":
                    self.type = CommandType.RECENT
                elif text == ".undo":
                    self.type = CommandType.UNDO
                elif text == ".rb":
                    self.type = CommandType.SHOW_REBRICKABLE
                elif text[0:6] == ".note ":
                    self.note = text[6:]
                    self.type = CommandType.NOTE
                elif text == ".help" or text == "help":
                    self.type = None
                else:
                    self.type = CommandType.SEARCH

        try:
            self.quantity = int(self.quantity)
        except ValueError:
            self.quantity = default_quantity


if __name__ == "__main__":
    last_part = None
    last_color = None
    note = None

    last_note = helpers.query(
        "select notes from part_transactions order by rowid desc limit 1"
    )

    if last_note and last_note[0] and last_note[0][0]:
        note = last_note[0][0]

    while True:
        if last_part or last_color:
            print("Current part/color: %s %s" % (last_color, last_part.encode('ascii','ignore').decode()))
        else:
            print(help)
        if note:
            print("Current Note: %s" % note)

        command = Command(input("> "), default_part=last_part, default_color=last_color)

        if not command.type:
            print(help)

        if command.type == CommandType.NOTE:
            note = command.note

        if command.type == CommandType.UNDO:
            helpers.query(
                "delete from part_transactions where rowid = (select max(rowid) from part_transactions)"
            )
            command.type = CommandType.RECENT

        if command.type == CommandType.SHOW_REBRICKABLE:
            subprocess.run(
                [
                    "firefox",
                    "https://rebrickable.com/parts/"
                    + helpers.search_part(last_part)[0][0],
                ]
            )

        if command.type == CommandType.RECENT:
            recent = helpers.query(
                "select quantity, colors.name, parts.name, notes from part_transactions join colors on colors.id = part_transactions.color_id join parts on parts.part_num = part_transactions.part_num order by date desc limit 20"
            )
            for t in recent:
                print("%d,%s,%s %s" % (t[0], t[1], t[2].encode('ascii','ignore').decode(), t[3]))

        if command.type == CommandType.SEARCH:
            print("Search results:")
            results = helpers.search_part(command.text)[:40]

            try:
                last_part = results[0][1]
            except IndexError:
                pass

            for part in results:
                print(f"{part[0]:<10} {part[1].encode('ascii','ignore').decode()}")

        if command.type == CommandType.SET_TRANSACTION:
            print(
                "Adding %d %s (%s)" % (command.quantity, command.set, command.set_num)
            )
            helpers.add_set(command.set_num, command.quantity, note)

        if command.type == CommandType.PART_TRANSACTION:
            last_part = command.part
            last_color = command.color

            if command.quantity != 0:
                print(
                    "Adding %d %s (%d) %s (%s)"
                    % (
                        command.quantity,
                        command.color,
                        command.color_id,
                        command.part.encode('ascii','ignore').decode(),
                        command.part_num,
                    )
                )
                helpers.add_part(
                    command.part_num, command.color_id, command.quantity, note
                )
            else:
                print("Nothing to add. Querying current part information...")
                print(
                    "Current quantity: %d"
                    % (helpers.get_part_total(command.part_num, command.color_id))
                )
