import pyfiglet
from arp import bot

ascii_art = pyfiglet.figlet_format("Net Scanner")

line_length = max(len(line) for line in ascii_art.split("\n"))

top_bottom_line = "-" * line_length

print(top_bottom_line)
print(ascii_art)
print(top_bottom_line)

bot.polling(non_stop=True)
