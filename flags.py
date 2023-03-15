import json
import random
from pathlib import Path
from sopel import plugin
from sopel import formatting

def green_text(s):
  return formatting.color(str(s), formatting.colors.GREEN)

def blue_text(s):
  return formatting.color(str(s), formatting.colors.BLUE)  

def yellow_text(s):
  return formatting.color(str(s), formatting.colors.YELLOW)  

# Show the hint and flag image
def show_message(bot, trigger):
  hint = bot.db.get_channel_value(trigger.sender, "flags_hint")
  bot.say(f"Guess this country | {hint}")

# Show the answer
def show_answer(bot, trigger):
  name = bot.db.get_channel_value(trigger.sender, "flags_name")
  bot.say(f"The answer was: {name}")  

# Show a hint
def show_hint(bot, trigger):
  name = bot.db.get_channel_value(trigger.sender, "flags_name")
  code = bot.db.get_channel_value(trigger.sender, "flags_code")
  letters = list(name)
  s = ""
  i = 1

  for letter in letters:
    if i == 1 or i == len(letters):
      s += green_text(letter)
    elif i == len(letters):
      s += " "
      s += green_text(letter)
    elif letter == " ":
      s += "  "
    else:
      s += " _"

    i += 1
  
  scode = green_text(code)
  s += f"  ({scode}) "

  bot.say(f"Hint: {s}")   

# Select a new country
def new_country(bot, trigger):
  # Load country info json (big)
  p = Path(__file__).parent.resolve()
  countries_file = open(p / Path("country_info.json"), "r")
  countries = json.load(countries_file)
  countries_file.close()

  # Choose a random coutnry
  country = random.choice(countries)

  # Choose which hint to show
  hint_number = random.randint(1, 5)
  hints = []

  if country["Capital"]:
    c = green_text("capital")
    s = country["Capital"]
    hints.append(f"The {c} is {s}")
  if country["Currency"]:
    c = green_text("currency")
    s = country["Currency"]
    hints.append(f"The {c} is {s}")
  if country["Languages"]:
    c = green_text("languages")
    s = country["Languages"]
    hints.append(f"The {c} are {s}")
  if country["Area KM2"]:
    c = green_text("area")
    s = country["Area KM2"]
    hints.append(f"The {c} is {s} km2")
  if country["Continent"]:
    c = green_text("continent")
    s = country["Continent"]
    hints.append(f"The {c} is {s}")

  hint = " | ".join(hints)
  
  # Save current country code in db
  bot.db.set_channel_value(trigger.sender, "flags_name", country["Country Name"])
  bot.db.set_channel_value(trigger.sender, "flags_code", country["ISO3"])
  bot.db.set_channel_value(trigger.sender, "flags_hint", hint)

  # Show the message
  show_message(bot, trigger)  

@plugin.command("country")
def show_country(bot, trigger):
  if trigger.group(2):
    s = trigger.group(2).strip().lower()
    if s == "skip":
      show_answer(bot, trigger)
      new_country(bot, trigger)
    elif s == "hint":
      show_hint(bot, trigger)
  else:
    show_message(bot, trigger)

@plugin.rule(".*")
def guess_country(bot, trigger):
  # If country selected try to guess or print message
  name = bot.db.get_channel_value(trigger.sender, "flags_name")

  if name:
    # If argument then try to guess
    line = trigger.group()
    if line:
      guess = line.strip().lower().replace(".", "")

      if name.lower().replace(".", "") in guess:
        green_name = green_text(name)
        c = f"{green_name} is correct!"
        bot.say(c)
        new_country(bot, trigger)
  else:
    new_country(bot, trigger)