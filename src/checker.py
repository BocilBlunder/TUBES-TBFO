import os
import sys

sys.setrecursionlimit(10000)

# Save PDA Information
start_input = ""
input_array = []
found = 0
accepted_config = []
productions = {}
states = []
symbols = []
stack_symbols = []
start_symbol = ""
stack_start = ""
acceptable_states = []
accept_with = ""
last_input = []
error_input = ""

# List of tokens
tokens = [
'</',
'-->',
'<!--',
'<', 
'>',
'html', 
'head', 
'body',
'alt=',
'any',
'title',
'link',
'href=',
'rel=',
'"',
"'",
'script',
'src=',
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
'abbr',
'strong',
'small',
'hr',
'img',
'form',
'method=',
'action=',
'POST',
'GET',
'button',
'type=',
'submit',
'reset',
'input',
'text',
'password',
'email',
'number',
'checkbox',
'p',
'b',
'a',
'em',
'id=',
'class=',
'style='
]

# Tokenize input
def tokenize(input):
    output = []

    prev_char = ''
    while (input != ""):
        found_token = False
        for token in tokens:
            # Acquire token
            if input.startswith(token) and (prev_char in [' ', '<', '>', '\n', '"', '</', "'"] and ((len(token) < len(input)) and (input[len(token):][0] in [' ', '<', '>', '\n', '"', "'"])) or (token in ['</', '<', '<!--', '-->'])):
                output.append(token)
                token_length = len(token)
                input = input[token_length:]
                found_token = True
                prev_char = token
                break

        # Acquire single character if token not found
        if (not(found_token)):
            if (not(input[0] == ' ' or input[0] == '\n')):
                output.append(input[0])
            prev_char = input[0]
            input = input[1:]

    return output

# Tokenize PDA
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

def generate(state, input, stack, config):
 global productions
 global found
 global last_input
 total = 0

 if found: 
  return 0

 if is_found(state, input, stack): # check if node can accept
  found = 1
  accepted_config.extend(config)
  return 1

 moves = get_moves(state, input, stack, config) # check for other possible moves
 if len(moves) == 0:
  if len(input) < len(last_input):
    last_input = input
  return 0

 for i in moves: # generate trees of each move
  total = total + generate(i[0], i[1], i[2], config + [(i[0], i[1], i[2])])  

 return total

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

   if len(current[0]) > 0: # read next token or character if still not empty
    if len(input) > 0 and (input[0] == current[0] or (current[0] == "any" and input[0] not in ['<', '>']) or (current[0] == "anyattr" and (input[0] not in ['"', "'"] or stack[0] != input[0]))):
     new.append(input[1:])
    else:
     continue
   else:   
    new.append(input)

   if len(current[1]) > 0: # read stack symbol
    if len(stack) > 0 and stack[0] == current[1]:
     new.append(current[2] + stack[1:])
    else:
     continue

   moves.append(new)

 return moves

# check if found
def is_found(state, input, stack):
 global accept_with
 global acceptable_states

 if len(input) > 0: 
  return 0

 if accept_with == "E": # accepts with empty stack
  if len(stack) == 1: # Z
   return 1

  return 0

 else:
  for i in acceptable_states:
   if i == state: # check if state is final state
    return 1

  return 0

# print config
def print_config(config):
 for i in config:
  print(i)

# parse pda file
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

 return 1

# search error
def search_error_location(file_path, error_input):
    error_input = error_input.replace(" ", "").replace("\t", "").replace("\n", "")
    with open(file_path, 'r') as file:
        lines = file.readlines()
        count = 0
        test_lines = lines
        while len(test_lines) > 0:
            joined = ''.join(test_lines).replace(" ", "").replace("\t", "").replace("\n", "")
            if error_input in joined:
                count += 1
            test_lines = test_lines[1:]
        print(f"Terjadi kesalahan pada line {count}:")
        print(lines[count - 1].strip())

# print verdict
def done():
 global error_input
 global last_input
 global html_path
 if found:
  print("Accepted") 
 else:
  print("Syntax Error.")
  for i in range(len(last_input)):
    if len(last_input) <= i:
        break
    else:
        error_input += last_input[i]
  search_error_location(html_path, error_input)

# main program
if len(sys.argv) != 3:
    print("Invalid parameters.")
    exit()

parse_file(sys.argv[1])
html_path = sys.argv[2]

with open(html_path, 'r') as html_file:
    start_input = html_file.read()
    input_array = tokenize(start_input) # tokenize html file
    last_input = start_input

if not generate(start_symbol, input_array, start_stack, [(start_symbol, input_array, start_stack)]):
    done()
else:
    done()