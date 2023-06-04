# SPLRE: Structural (Python/Perl)-Like Regular Expressions

splre is a bit of a toy project to make a slightly different regular expression syntax based off of the ideas of Rob Pike's structural regular expressions as used in sam, see: [this paper](http://doc.cat-v.org/bell_labs/structural_regexps/se.pdf)

The syntax I chose is a little different, with the hope it's more readable:
```
    $LOOPCMD[m:n:i]($REGEX):$FOLLOWCMDS for the "looping" commands,
    $MODCMD[m:n:i]($MODSTR) for the "change" commands,
    $SCMD for the single character commands.

    $LOOPCMDS:
        "x": "extract": Tokenise based on matching regular expressions
        "y": "inverse extract": Tokenise based on text *between* matching regular expressions
        "g": "guard": Execute the following commands based on if the token matches the regular expression
        "v": "inverse guard": Execute the following commands based on if the token *doesn't* match the regular expression
    $MODCMDS:
        "c": "change": Replace the token with $MODSTR
        "i": "insert": Return the concatenation of $MODSTR and the token
        "a": "append": Return the concatenation of the token and $MODSTR
    $SCMD:
        "p": "print": Print the current token
        "d": "delete": Delete the current token

    $FOLLOWCMDS can be either a single command of any type, or a sub-block within braces.
    All of the commands within the sub-block will be executed for each token of the parent in order.
    For example:
    
        x(\w*):             - tokenise the input string into tokens of "word-like" character
        {                   - for each token
            g(hello):c(bye) - if the token is "hello" replace it with "bye"
            g(bye):p        - if the token is "bye", print it. NOTE: "hello" tokens will already be "bye" tokens.
        }
```
A more complete spec is [here](regexspec.md)

Currently, there are two python files: 
[splre.py](splre.py) contains the actual regular expression parser, as well as a sort of REPL for testing the language. It leans heavily on python's re library and [parsimonious](https://github.com/erikrose/parsimonious). So far, I haven't added any capture group functionality even though it should have it, and the regex strings are just directly plugged into python's stuff.
[splgrep.py](splgrep.py) is a limited grep-like program that imports the splre stuff from the previous file and takes input either from stdin or from a single file and gives you the output. It has a verbose option as well to see the parse tree and grammar. This *does* have issues with shell splitting and escaping so make sure to quote the splre strings (there is also only one positional argument for the splre string) and use prodigious back spacing for escape characters - they don't seem to work correctly yet in any case.

Using Python's re isn't ideal, as one of the key ideas of structure regular expressions is not assuming anything about the shape of the text - i.e.: is it line-based. This is why it only really makes sense to talk about the matches in terms of "tokens" - the input to the regular expression being a single token of a UTF-8 byte stream. Parsimonious is also a little heavy handed for just a regular expression language, so I'll probably replace it with a custom recursive decent parser when it's more finished, but it's flexible enough for now.

The end goal of this is to hook this into my lisp-like shell language (LISSH - not good enough to upload yet) to make a lispy language that is decent for text processing. Something like:
```
    ({x(def (func_name:\w+)):{
        g(lissh):(define py_$(func_name) (...))
    }})
```
For each python function definition, define a function `py_$func_name` if the `$func_name` contains `"lissh"`.
