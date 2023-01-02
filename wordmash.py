# 123
import json
import random
from pathlib import Path
from sopel import plugin
from sopel import formatting
from itertools import permutations

def green_text(s):
  return formatting.color(str(s), formatting.colors.GREEN)

def blue_text(s):
  return formatting.color(str(s), formatting.colors.BLUE)  

def yellow_text(s):
  return formatting.color(str(s), formatting.colors.YELLOW)  

def get_random_words():
  words = get_words()
  rkey = random.choice(list(words))
  rkl = len(rkey)
  skl = "".join(sorted(rkey))
  wordlist = [rkey]

  for key in words:
    if key in wordlist:
      continue
    if len(key) == rkl:
      srt = "".join(sorted(key))
      if srt == skl:
        wordlist.append(key)

  return wordlist

def get_scramble(random_words):
  perms = list(set([''.join(p) for p in permutations(random_words[0])]))
  random.shuffle(perms)
  for p in perms:
    if p not in random_words:
      return p
  return perms[0]

def select_words(bot):
  state = get_state()
  random_words = get_random_words()
  state["current_words"] = random_words
  w = random_words[0]

  wl = list(w)
  random.shuffle(wl)
  scramble = get_scramble(random_words)
  state["current_scramble"] = scramble

  obj = json.dumps(state)
  p = Path(__file__).parent.resolve()
  fstate = open(p / Path("wordmash_state.json"), "w")
  fstate.write(obj)
  fstate.close() 

  ss = green_text(scramble)
  bot.say(f"Yum! A new mash is served. Enjoy your {ss}!")

def on_match(bot, trigger, word):
  p = Path(__file__).parent.resolve()
  fpoints = open(p / Path("wordmash_points.json"), "r")
  points = json.load(fpoints)
  fpoints.close()
  fpoints = open(p / Path("wordmash_points.json"), "w")
  nick = str(trigger.nick)
  if nick in points:
    pts = points[nick] + 1
  else:
    pts = 1
  points[nick] = pts
  obj = json.dumps(points)
  fpoints.write(obj)
  fpoints.close()

  definition = get_word_definition(word)
  ns = blue_text(nick)
  np = yellow_text(pts)
  dw = green_text(word)
  df = green_text(definition + ".")
  bot.say(f"Correct {ns} ! {dw}: {df} You gain an internet point, making your total {np}")
  select_words(bot) 

def get_words():
  p = Path(__file__).parent.resolve()
  fwords = open(p / Path("words.json"), "r")
  words = json.load(fwords)
  return words

def get_state():
  p = Path(__file__).parent.resolve()
  fstate = open(p / Path("wordmash_state.json"), "r")
  state = json.load(fstate)
  fstate.close()
  return state 

def get_word_definition(word):
  words = get_words()
  return words[word]

def sort_string(s):
  return ''.join(sorted(s))

def stop_mash(bot, word):
  definition = get_word_definition(word)
  dw = green_text(word)
  df = green_text(definition + ".")
  bot.say(f"Stopping the mash. A correct solution was: {dw}: {df}")
  select_words(bot)   

@plugin.command('wordmash')
def wordmash(bot, trigger):
  state = get_state()
  if len(state["current_words"]) == 0:
    select_words(bot)
  else:
    current_words = state["current_words"]
    current_scramble = state["current_scramble"]

    if trigger.group(2):
      word = trigger.group(2).strip().lower()
      nick = str(trigger.nick)
      
      if word == "!stop":
        stop_mash(bot, current_words[0])
      elif len(word) != len(current_words[0]):
        ns = blue_text(nick)
        bot.say(f"There's an incorrect number of letters in your guess, {ns}! Try again.")
      elif sort_string(word) != sort_string(current_words[0]):
        ns = blue_text(nick)
        bot.say(f"You're not using the letters from the mash, {ns}! Try again.")
      else:
        for w in current_words:
          if word == w:
            on_match(bot, trigger, word)
            break
    else:
      ns = green_text(current_scramble)
      bot.say(f"The current mash is: {ns}")