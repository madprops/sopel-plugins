import json
import random
from pathlib import Path
from sopel import plugin

# Show the hint and flag image
def show_message(bot, trigger):
  hint = bot.db.get_channel_value(trigger.sender, "flags_hint")
  flag = bot.db.get_channel_value(trigger.sender, "flags_flag")
  bot.say(f"{hint} | {flag}")

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

  if hint_number == 1:
    s = country["Capital"] or "unknown"
    hint = f"The capital of this country is {s}"
  elif hint_number == 2:
    s = country["Currency"] or "unknown"
    hint = f"The currency of this country is {s}"
  elif hint_number == 3:
    s = country["Languages"] or "unknown"
    hint = f"The languages of this country are {s}"
  elif hint_number == 4:
    s = country["Area KM2"] or "unknown"
    hint = f"The area (km2) of this country is {s}"
  elif hint_number == 5:
    s = country["Continent"] or "unknown"
    hint = f"The continent of this country is {s}"
  
  c = country["ISO2"].lower()
  flag = f"http://w.merkoba.com/flags/{c}.png"

  # Save current country code in db
  bot.db.set_channel_value(trigger.sender, "flags_name", country["Country Name"])
  bot.db.set_channel_value(trigger.sender, "flags_code", country["ISO2"])
  bot.db.set_channel_value(trigger.sender, "flags_hint", hint)
  bot.db.set_channel_value(trigger.sender, "flags_flag", flag)

  # Show the message
  show_message(bot, trigger)  

@plugin.command("flag")
def show_flag(bot, trigger):
  show_message(bot, trigger)

@plugin.rule(".*")
def guess_flag(bot, trigger):
  # If country selected try to guess or print message
  name = bot.db.get_channel_value(trigger.sender, "flags_name")

  if name:
    # If argument then try to guess
    line = trigger.group()
    if line:
      guess = line.strip().lower()
      if name.lower() == guess:
        bot.say("Correct!")
        new_country(bot, trigger)
  else:
    new_country(bot, trigger)