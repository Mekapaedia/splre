x[n:m:i](...):{cmds} turn input [nth to mth incrementing by i] into n tokens matching regex ...
y[n:m:i](...):{cmds} turn input [nth to mth incrementing by i] into n tokens in between matching regex ...
g[n:m:i](...):{cmds} if token in [n to m incrementing by i] matches regex ... run cmds
v[n:m:i](...):{cmds} if token in [n to m incrementing by i] doesn't match ... run cmds
c(...) change token to ...
i(...) insert ... to start of token
a(...) insert ... to end of token
p print current token
d delete current token
(...) function call
ex:
replace Fizz with Buzz
x("Fizz"):c("Buzz")
or 
x("Fizz"): {
    c("Buzz")
}
regex string:
\ escape:
  \\ backslash
  \a bell
  \b backspace
  \c$CHAR control-$CHAR
  \e escape
  \f form feed
  \n linefeed
  \r carriage return
  \t tab 
  \v vertical tab
  \xhhh... literal hex character hhh...
  \U+hhh... unicode hex point hhh...
  \p(...) unicode character category property, negated with ^, or'd with |
  \bd(...) unicode bidi class, negated with ^, or'd with |
  \d digit
  \D NOT digit
  \s whitespace
  \S NOT whitespace
  \w "word" - alnum and _
  \W NOT "word" - anything but alnum and _
  \- literal "-" in a character set
^ start of token
$ end of token
. any character
[...] character class ...
| or
* 0 or more (greedy)
+ 1 or more (greedy)
? 0 or 1 (greedy)
*? 0 or more (minimal)
+? 0 or more (minimal)
?? 0 or 1 (minimal)
*+ 0 or more (possessive)
++ 1 or more (possessive)
?+ 0 or 1 (possessive)
{m} m repetitions
{m,n} m to n repetitions (greedy)
{m,n}? m to n repetitions (minimal)
{m,n}+ m to n repetitions (possessive)
capture groups in regex strings:
  (name:...) capture group "name" matching "..."
  (name:?>=...) positive lookahead
  (name:?>!...) negative lookahead
  (name:?<=...) positive lookbehind
  (name:?<!...) negative lookbehind
capture groups in replacement strings:
  (name) capture group "name"
