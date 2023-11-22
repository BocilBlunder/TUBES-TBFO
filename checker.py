import os
import sys

sys.setrecursionlimit(10000)

start_input = ""
input_array = []
found = 0 # stores found state
accepted_config = [] # here we will post end configuration that was accepted

productions = {}

states = []

symbols = []

stack_symbols = []

start_symbol = ""

stack_start = ""

acceptable_states = []

tokens = [
'</',
'<', 
'>',
'html', 
'head', 
'body',
'any',
'title',
'link=',
'href=',
'rel=',
'"',
'script',
'src=',
'p',
'h1',
'h2',
'h3',
'h4',
'h5',
'h6',
'table',
'tr',
'th',
'td',
'br',
'div',
'em',
'b',
'abbr',
'strong',
'small',
'a',
'href=',
'hr'
]

# E - accept on empty stack or F - acceptable state (default is false)
accept_with = ""

def tokenize(input):
    output = []

    prev_char = ''
    while (input != ""):
        found_token = False
        for token in tokens:
            if input.startswith(token) and (prev_char in [' ', '<', '>', '\n', '"', '</'] and ((len(token) < len(input)) and (input[len(token):][0] in [' ', '<', '>', '\n', '"'])) or (token in ['</', '<'])):
                output.append(token)
                token_length = len(token)
                input = input[token_length:]
                found_token = True
                prev_char = token
                break

        if (not(found_token)):
            if (not(input[0] == ' ' or input[0] == '\n')):
                output.append(input[0])
            prev_char = input[0]
            input = input[1:]

    return output

def tokenize_pda(input):
    output = []

    while (input != ""):
        found_token = False
        for token in tokens:
            if input.startswith(token):
                output.append(token)
                token_length = len(token)
                input = input[token_length:]
                found_token = True
                break

        if (not(found_token)):
            if (not(input[0] == ' ' or input[0] == '\n')):
                output.append(input[0])
            input = input[1:]

    return output

# recursively generate all prossiblity tree and terminate on success
def generate(state, input, stack, config):
 global productions
 global found
 total = 0

 # check for other tree node sucess
 if found:
  return 0

 # check if our node can terminate with success
 if is_found(state, input, stack):
  found = 1 # mark that word is accepted so other tree nodes know and terminate

  # add successful configuration
  accepted_config.extend(config)

  return 1

 # check if there are further moves (or we have to terminate)
 moves = get_moves(state, input, stack, config)
 if len(moves) == 0:
  return 0

 # for each move do a tree
 for i in moves:
  total = total + generate(i[0], i[1], i[2], config + [(i[0], i[1], i[2])])  

 return total


# checks if symbol is terminal or non-terminal
def get_moves(state, input, stack, config):
 global productions
 moves = []

 for i in productions:

  if i != state:
   continue

  for j in productions[i]:
   current = j
   new = []

   new.append(current[3])

   # read symbol from input if we have one
   if len(current[0]) > 0:
    if len(input) > 0 and (input[0] == current[0] or (current[0] == "any" and input[0] not in ['<', '>'])):
     new.append(input[1:])
    else:
     continue
   else:   
    new.append(input)

   # read stack symbol
   if len(current[1]) > 0:
    if len(stack) > 0 and stack[0] == current[1]:
     new.append(current[2] + stack[1:])
    else:
     continue

   moves.append(new)

 return moves


# checks if word already was generated somewhere in past
def is_found(state, input, stack):
 global accept_with
 global acceptable_states

 # check if all symbols are read
 if len(input) > 0: 
  return 0

 # check if we accept with empty stack or end state
 if accept_with == "E":
  if len(stack) == 1:  # accept if stack is empty
   return 1

  return 0

 else:
  for i in acceptable_states:
   if i == state: # accept if we are in terminal state
    return 1

  return 0

def print_config(config):
 for i in config:
  print(i)


def parse_file(filename):
 global productions
 global start_symbol
 global start_stack
 global acceptable_states
 global accept_with

 try:
  lines = [line.rstrip() for line in open(filename)]
 except:
  return 0

 start_symbol = lines[3]

 start_stack = [lines[4]]

 acceptable_states.extend(lines[5].split())

 accept_with = lines[6] 

 for i in range(7, len(lines)):
  production = lines[i].split()

  configuration = [(production[1], production[2], tokenize_pda(production[4]), production[3])]

  if not production[0] in productions.keys(): 
   productions[production[0]] = []

  configuration = [tuple(s if (s != "e" and s != ["e"]) else ("" if s == "e" else []) for s in tup) for tup in configuration]

  productions[production[0]].extend(configuration)

 print (productions)
 print (start_symbol)
 print (start_stack)
 print (acceptable_states)
 print (accept_with)

 return 1

def done():
 if found:
  print("Hurray! Input:\n" + start_input + "\nis part of grammar.") 
 else:
  print("Sorry! Input:\n" + start_input + "\nis not part of grammar.") 


if len(sys.argv) != 3:
    print("Invalid parameters. Usage: python3 checker.py pda.txt test.html")
    exit()

parse_file(sys.argv[1])

with open(sys.argv[2], 'r') as html_file:
    start_input = html_file.read()
    input_array = tokenize(start_input)

if not generate(start_symbol, input_array, start_stack, [(start_symbol, input_array, start_stack)]):
    print_config(accepted_config)
    done()
else:
    print_config(accepted_config)
    done()

print(input_array)
print(start_stack)