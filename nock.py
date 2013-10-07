# -*- coding: utf-8 -*-
"""nock -- working through http://www.urbit.org/2013/08/22/Chapter-2-nock.html

N.B. Implementation functions have a `_` prefix. Public functions do not. Don't worry to much about it. Just use the prefix-less versions when playing around, as they have all the debug niceties.
"""
import re
import collections
import contextlib
import logging

logger = logging.getLogger('nock')
DEFAULT_LEVEL = logger.getEffectiveLevel()
__all__ = ['YES', 'NO', 'fas', 'lus', 'nock', 'tar', 'tis', 'wut',
           'debug']

"""
1 Structures

  A noun is an atom or a cell.  An atom is any natural number.
  A cell is an ordered pair of nouns.

2 Reductions

  1  :: nock(a)           *a
  2  :: [a b c]           [a [b c]]
  3
  4  :: ?[a b]            0
  5  :: ?a                1
  6  :: +[a b]            +[a b]
  7  :: +a                1 + a
  8  :: =[a a]            0
  9  :: =[a b]            1
  10 :: =a                =a
  11
  12 :: /[1 a]            a
  13 :: /[2 a b]          a
  14 :: /[3 a b]          b
  15 :: /[(a + a) b]      /[2 /[a b]]
  16 :: /[(a + a + 1) b]  /[3 /[a b]]
  17 :: /a                /a
  18
  19 :: *[a [b c] d]      [*[a b c] *[a d]]
  20
  21 :: *[a 0 b]          /[b a]
  22 :: *[a 1 b]          b
  23 :: *[a 2 b c]        *[*[a b] *[a c]]
  24 :: *[a 3 b]          ?*[a b]
  25 :: *[a 4 b]          +*[a b]
  26 :: *[a 5 b]          =*[a b]
  27
  28 :: *[a 6 b c d]      *[a 2 [0 1] 2 [1 c d] [1 0] 2 [1 2 3] [1 0] 4 4 b]
  29 :: *[a 7 b c]        *[a 2 b 1 c]
  30 :: *[a 8 b c]        *[a 7 [[7 [0 1] b] 0 1] c]
  31 :: *[a 9 b c]        *[a 7 c 2 [0 1] 0 b]
  32 :: *[a 10 [b c] d]   *[a 8 c 7 [0 3] d]
  33 :: *[a 10 b c]       *[a c]
  34
  35 :: *a                *a


1. Structures
=============

    A noun is an atom or a cell.  An atom is any natural number.
    A cell is any ordered pair of nouns.

Nouns are the dumbest data model ever. Nouns make JSON look like XML and XML look like ASN.1. It may also remind you of Lisp’s S-expressions - you can think of nouns as “S-expressions without the S.”

To be exact, a noun is an S-expression, except that classic S-expressions have multiple atom types (”S” is for “symbol”). Since Nock is designed to be used with a higher-level type system (such as Hoon’s), it does not need low-level types. An atom is just an unsigned integer of any size.

For instance, it’s common to represent strings (or even whole text files) as atoms, arranging them LSB first - so “foo” becomes 0x6f6f66. How do we know to print this as “foo”, not 0x6f6f66? We need external information - such as a Hoon type. Similarly, other common atomic types - signed integers, floating point, etc - are all straightforward to map into atoms.

It’s also important to note that, unlike Lisp, Nock cannot create cyclical data structures. It is normal and common for nouns in a Nock runtime system to have acyclic structure - shared subtrees. But there is no Nock computatioen that can make a child point to its parent. One consequence: Nock has no garbage collector. (Nor can dag structure be detected, as with Lisp eq.)

There is also no single syntax for nouns. If you have nouns you have Nock; if you have Nock you have Hoon; if you have Hoon, you can write whatever parser you like.

Let’s continue:

2. Pseudocode
=============

It’s important to recognize that the pseudocode of the Nock spec is just that: pseudocode. It looks a little like Hoon. It isn’t Hoon - it’s just pseudocode. Or in other words, just English. At the bottom of every formal system is a system of axioms, which can only be written in English. (Why pseudocode, not Hoon? Since Hoon is defined in Nock, this would only give a false impression of nonexistent precision.)

The logic of this pseudocode is a pattern-matching reduction, matching from the top down. To compute Nock, repeatedly reduce with the first line that matches. Let’s jump right in!

Line 1:
-------

    1  ::    nock(a)           *a

Nock is a pure (stateless) function from noun to noun. In our pseudocode (and only in our pseudocode) we express this with the prefix operator `*`.

This function is defined for every noun, but on many nouns it does nothing useful. For instance, if `a` is an atom, `*a` reduces to… `*a`. In theory, this means that Nock spins forever in an infinite loop. In other words, Nock produces no result - and in practice, your interpreter will stop.

(Another way to see this is that Nock has “crash-only” semantics. There is no exception mechanism. The only way to catch Nock errors is to simulate Nock in a higher-level virtual Nock - which, in fact, we do all the time. A simulator (or a practical low-level interpreter) can report, out of band, that Nock would not terminate. It cannot recognize all infinite loops, of course, but it can catch the obvious ones - like `*42`.)

Normally `a` in `nock(a)` is a cell `[s f]`, or as we say

    [subject formula]

Intuitively, the formula is your function and the subject is its argument. We call them something different because Hoon, or any other high-level language built on Nock, will build its own function calling convention which does not map directly to *[subject formula].


Line 2:
-------

    2  ::    [a b c]           [a [b c]]

"""


def _aorc(a):
    """Return an atom or a properly structured cell.

    >>> _aorc(1)
    1
    >>> _aorc((1, 2))
    (1, 2)
    """
    if isinstance(a, collections.Iterable):
        return _t(*a)
    else:
        return a


def _t(*lst):
    """Properly structure an improper list.

    2  ::    [a b c]           [a [b c]]

    >>> _t(1)
    (1, 0)
    >>> _t(1, 2)
    (1, 2)
    >>> _t(1, 2, 3)
    (1, (2, 3))
    >>> _t(1, 2, 3, 4)
    (1, (2, (3, 4)))
    >>> _t(42, ((4, 0, 1), (3, 0, 1)))
    (42, ((4, (0, 1)), (3, (0, 1))))
    """
    if len(lst) == 1:
        return (_aorc(lst[0]), 0)
    elif len(lst) == 2:
        a, b = lst
        return (_aorc(a), _aorc(b))
    else:
        return (_aorc(lst[0]), _t(*lst[1:]))


"""
Ie, brackets (in our pseudocode, as in Hoon) associate to the right. For those with Lisp experience, it’s important to note that Nock and Hoon use tuples or “improper lists” much more heavily than Lisp. The list terminator, normally 0, is never automatic. So the Lisp list

    (a b c)

becomes the Nock noun

    [a b c 0]

which is equivalent to

    [a [b [c 0]]]

Note that we can and do use unnecessary brackets anyway, for emphasis.

Let’s move on to the axiomatic functions.

Lines 4-9:
----------

    4  ::    ?[a b]            0
    5  ::    ?a                1
    6  ::    +[a b]            +[a b]
    7  ::    +a                1 + a
    8  ::    =[a a]            0
    9  ::    =[a b]            1

Here we define more pseudocode operators, which we’ll use in reductions further down. So far we have four built-in functions: `*` meaning Nock itself, `?` testing whether a noun is a cell or an atom, `+` incrementing an atom, and `=` testing for equality. Again, no rocket science here.

We should note that in Nock and Hoon, `0` (pronounced “yes”) is true, and `1` (“no”) is false. Why? It’s fresh, it’s different, it’s new. And it’s annoying. And it keeps you on your toes. And it’s also just intuitively right.
"""
YES = 0
NO  = 1


def _wut(noun):
    """? :: Test whether a noun is a cell or an atom.

    4  ::    ?[a b]            0
    5  ::    ?a                1

    >>> wut((1, 2))
    0
    >>> wut(1)
    1
    """
    return NO if isinstance(noun, int) else YES


def _lus(noun):
    """+ :: Increment an atom.

    6  ::    +[a b]            +[a b]
    7  ::    +a                1 + a

    >>> lus((1, 2))
    (1, 2)
    >>> lus(1)
    2
    """
    return (1 + noun) if isinstance(noun, int) else noun


def _tis(noun):
    """= :: test for equality

    8  ::    =[a a]            0
    9  ::    =[a b]            1

    >>> tis((1, 1))
    0
    >>> tis((1, 0))
    1
    """
    return YES if noun[0] == noun[1] else NO


"""
Lines 12-16:
------------

    12 ::    /[1 a]            a
    13 ::    /[2 a b]          a
    14 ::    /[3 a b]          b
    15 ::    /[(a + a) b]      /[2 /[a b]]
    16 ::    /[(a + a + 1) b]  /[3 /[a b]]

Slightly more interesting is our tree numbering. Every noun is of course a tree. The / operator - pronounced “slot” - imposes an address space on that tree, mapping every nonzero atom to a tree position.

1 is the root. The head of every node n is 2n; the tail is 2n+1. Thus a simple tree:

         1
      2      3
    4   5  6   7
             14 15

If the value of every leaf is its tree address, this tree is

    [[4 5] [6 14 15]]

and, for some examples of addressing:

    /[1 [[4 5] [6 14 15]]]

is `[[4 5] [6 14 15]]]`

    /[2 [[4 5] [6 14 15]]]

is `[4 5]`

    /[3 [[4 5] [6 14 15]]]

is `[6 14 15]`, and

    /[7 [[4 5] [6 14 15]]]

is `[14 15]`

I do hope this isn’t so terribly hard to follow.
"""


def _fas((n, noun)):
    """Return the specified slot from the given noun.

    12 ::    /[1 a]            a
    13 ::    /[2 a b]          a
    14 ::    /[3 a b]          b
    15 ::    /[(a + a) b]      /[2 /[a b]]
    16 ::    /[(a + a + 1) b]  /[3 /[a b]]

    >>> tree = ((4, 5), (6, 14, 15))
    >>> fas((1, tree))
    ((4, 5), (6, (14, 15)))
    >>> fas((2, tree))
    (4, 5)
    >>> fas((3, tree))
    (6, (14, 15))
    >>> fas((7, tree))
    (14, 15)
    """
    noun = _aorc(noun)
    try:
        if n == 1:
            return noun
        elif n == 2:
            return noun[0]
        elif n == 3:
            return noun[1]
        elif n % 2 == 0:  # even
            return _fas((2, _fas((n // 2, noun))))
        elif n % 2 == 1:  # odd
            return _fas((3, _fas(((n - 1) // 2, noun))))
        else:
            return noun
    except TypeError:
        return noun


"""
Line 21:
--------

Now we enter the definition of Nock itself - ie, the `*` operator.

    21 ::    *[a 0 b]          /[b a]

`0` is simply Nock’s tree-addressing operator. Let’s try it out from the Arvo command line.

Note that we’re using Hoon syntax here. Since we do not use Nock from Hoon all that often (it’s sort of like embedding assembly in C), we’ve left it a little cumbersome. In Hoon, instead of writing `*[a 0 b]`, we write

    .*(a [0 b])

So, to reuse our slot example, let’s try the interpreter:

    ~tasfyn-partyv> .*([[4 5] [6 14 15]] [0 7])

gives, while the sky remains blue and the sun rises in the east:

    [14 15]

Even stupider is line 22:

Line 22:
--------

    22 ::    *[a 1 b]          b

1 is the constant operator. It produces its argument without reference to the subject. So

    ~tasfyn-partyv> .*(42 [1 153 218])

yields

    [153 218]

Line 23:
--------

    23 ::    *[a 2 b c]        *[*[a b] *[a c]]

Line 23 brings us the essential magic of recursion. 2 is the Nock operator. If you can compute a subject and a formula, you can evaluate them in the interpreter. In most fundamental languages, like Lisp, eval is a curiosity. But Nock has no apply - so all our work gets done with 2.

Let’s convert the previous example into a stupid use of 2:

    ~tasfyn-partyv> .*(77 [2 [1 42] [1 1 153 218]])

with a constant subject and a constant formula, gives the same

    [153 218]

Like so:

    *[77 [2 [1 42] [1 1 153 218]]

    23 ::    *[a 2 b c]        *[*[a b] *[a c]]

    *[*[77 [1 42]] *[77 [1 1 153 218]]]

    21 ::    *[a 1 b]          b

    *[42 *[77 [1 1 153 218]]]

    *[42 1 153 218]

    [153 218]

Lines 24-25:
------------

    24 ::    *[a 3 b]          ?*[a b]
    25 ::    *[a 4 b]          +*[a b]
    26 ::    *[a 5 b]          =*[a b]

In lines 25-26, we meet our axiomatic functions again:

For instance, if `x` is a formula that calculates some product, `[4 x]` calculates that product plus one. Hence:

    ~tasfyn-partyv> .*(57 [0 1])
    57

and

    ~tasfyn-partyv> .*([132 19] [0 3])
    19

and

    ~tasfyn-partyv> .*(57 [4 0 1])
    58

and

    ~tasfyn-partyv> .*([132 19] [4 0 3])
    20


Line 19:
--------

    19 ::    *[a [b c] d]      [*[a b c] *[a d]]

Um, what?

Since Nock of an atom just crashes, the practical domain of the Nock function is always a cell. Conventionally, the head of this cell is the “subject,” the tail is the “formula,” and the result of Nocking it is the “product.” Basically, the subject is your data and the formula is your code.

We could write line 19 less formally:

    *[subject [formula-x formula-y]]
    =>  [*[subject formula-x] *[subject formula-y]]

In other words, if you have two Nock formulas `x` and `y`, a formula that computes the pair of them is just `[x y]`. We can recognize this because no atom is a valid formula, and every formula that does not use line 19 has an atomic head.

If you know Lisp, you can think of this feature as a sort of “implicit cons.” Where in Lisp you would write `(cons x y)`, in Nock you write `[x y]`.

For example,

    ~tasfyn-partyv> .*(42 [4 0 1])

where `42` is the subject (data) and `[4 0 1]` is the formula (code), happens to evaluate to `43`. Whereas

    ~tasfyn-partyv> .*(42 [3 0 1])

is `1`. So if we evaluate

    ~tasfyn-partyv> .*(42 [[4 0 1] [3 0 1]])

we get

    [43 1]

Except for the crash defaults (lines 6, 10, 17, and 35), we’ve actually completed all the essential aspects of Nock. The operators up through 5 provide all necessary computational functionality. Nock, though very simple, is actually much more complex than it formally needs to be.

Operators 6 through 10 are macros. They exist because Nock is not a toy, but a practical interpreter. Let’s see them all together:

Lines 28-33:
------------

    28 ::    *[a 6 b c d]      *[a 2 [0 1] 2 [1 c d] [1 0] 2 [1 2 3] [1 0] 4 4 b]
    29 ::    *[a 7 b c]        *[a 2 b 1 c]
    30 ::    *[a 8 b c]        *[a 7 [[7 [0 1] b] 0 1] c]
    31 ::    *[a 9 b c]        *[a 7 c 2 [0 1] 0 b]
    32 ::    *[a 10 [b c] d]   *[a 8 c 7 [0 3] d]
    33 ::    *[a 10 b c]       *[a c]

Whoa! Have we entered rocket-science territory? Let’s try to figure out what these strange formulas do - simplest first. The simplest is clearly line 33:

    33 ::    *[a 10 b c]       *[a c]

If `x` is an atom and `y` is a formula, the formula `[10 x y]` appears to be equivalent to… `y`. For instance:

    ~tasfyn-partyv> .*([132 19] [10 37 [4 0 3]])
    20

Why would we want to do this? `10` is actually a hint operator. The `37` in this example is discarded information - it is not used, formally, in the computation. It may help the interpreter compute the expression more efficiently, however.

Every Nock computes the same result - but not all at the same speed. What hints are supported? What do they do? Hints are a higher-level convention which do not, and should not, appear in the Nock spec. Some are defined in Hoon. Indeed, a naive Nock interpreter not optimized for Hoon will run Hoon quite poorly. When it gets the product, however, the product will be right.

There is another reduction for hints - line 32:

    32 ::    *[a 10 [b c] d]   *[a 8 c 7 [0 3] d]

Once we see what `7` and 8 do, we’ll see that this complex hint throws away an arbitrary `b`, but computes the formula `c` against the subject and… throws away the product. This formula is simply equivalent to `d`. Of course, in practice the product of `c` will be put to some sordid and useful use. It could even wind up as a side effect, though we try not to get that sordid.

(Why do we even care that `c` is computed? Because `c` could crash. A correct Nock cannot simply ignore it, and treat both variants of `10` as equivalent.)

We move on to the next simplest operator, 7. Line 29:

    29 ::    *[a 7 b c]        *[a 2 b 1 c]

Suppose we have two formulas, `b` and `c`. What is the formula `[7 b c]`? This example will show you:

    ~tasfyn-partyv> .*(42 [7 [4 0 1] [4 0 1]])
    44

`7` is an old mathematical friend, function composition. It’s easy to see how this is built out of `2`. The data to evaluate is simply `b`, and the formula is `c` quoted.

Line 30 looks very similar:

    30 ::    *[a 8 b c]        *[a 7 [[7 [0 1] b] 0 1] c]

Indeed, `8` is `7`, except that the subject for `c` is not simply the product of `b`, but the ordered pair of the product of `b` and the original subject. Hence:

    ~tasfyn-partyv> .*(42 [8 [4 0 1] [0 1]])
    [43 42]

and

    ~tasfyn-partyv> .*(42 [8 [4 0 1] [4 0 3]])
    43

Why would we want to do this? Imagine a higher-level language in which the programmer declares a variable. This language is likely to generate an `8`, because the variable is computed against the present subject, and used in a calculation which depends both on the original subject and the new variable.

For extra credit, explain why we can’t just define

    *[a 8 b c]        *[a 7 [b 0 1] c]

Another simple macro is line 31:

    31 ::    *[a 9 b c]        *[a 7 c 2 [0 1] 0 b]

`9` is a calling convention. With `c`, we produce a noun which contains both code and data - a core. We use this core as the subject, and apply the formula within it at slot `b`.

And finally, we come to the piece de resistance - line 28:

    28 ::    *[a 6 b c d]      *[a 2 [0 1] 2 [1 c d] [1 0] 2 [1 2 3] [1 0] 4 4 b]

Great giblets! WTF is this doing? It seems we’ve finally arrived at some real rocket science.

Actually, `6` is a primitive known to every programmer - good old “if.” If `b` evaluates to `0`, we produce `c`; if `b` evaluates to `1`, we produce `d`; otherwise, we crash.

For instance:

    ~tasfyn-partyv> .*(42 [6 [1 0] [4 0 1] [1 233]])
    43

and

    ~tasfyn-partyv> .*(42 [6 [1 1] [4 0 1] [1 233]])
    233

In real life, of course, the Nock implementor knows that `6` is “if” and implements it as such. There is no practical sense in reducing through this macro, or any of the others. We could have defined “if” as a built-in function, like increment - except that we can write “if” as a macro. If a funky macro.

It’s a good exercise, however, to peek inside the funk.

We can actually simplify the semantics of `6`, at the expense of breaking the system a little, by creating a macro that works as “if” only if `b` is a proper boolean and produces `0` or `1`. Perhaps we have a higher-level type system which checks this.

This simpler “if” would be:

    *[a 6 b c d]    *[a [2 [0 1] [2 [1 c d] [[1 0] [4 4 b]]]]]

Or without so many unnecessary brackets:

    *[a 6 b c d]    *[a 2 [0 1] 2 [1 c d] [1 0] [4 4 b]]

How does this work? We’ve replaced `[6 b c d]` with the formula `[2 [0 1] [2 [1 c d] [[1 0] [4 4 b]]]]`. We see two uses of `2`, our evaluation operator - an outer and an inner.

Call the inner one `i`. So we have `[2 [0 1] i]`. Which means that, to calculate our product, we use `[0 1]` - that is, the original subject - as the subject; and the product of `i` as the formula.

Okay, cool. So `i` is `[2 [1 c d] [[1 0] [4 4 b]]]`. We compute Nock with subject `[1 c d]`, formula `[[1 0] [4 4 b]]`.

Obviously, `[1 c d]` produces just `[c d]` - that is, the ordered pair of the “then” and “else” formulas. `[[1 0] [4 4 b]]` is a line 19 cell - its head is `[1 0]`, producing just `0`, its tail `[4 4 b]`, producing… what? Well, if `[4 b]` is `b` plus `1`, `[4 4 b]` is `b` plus `2`.

We’re assuming that `b` produces either `0` or `1`. So `[4 4 b]` yields either `2` or `3`. `[[1 0] [4 4 b]]` is either `[0 2]` or `[0 3]`. Applied to the subject `[c d]`, this gives us either `c` or `d` - the product of our inner evaluation `i`. This is applied to the original subject, and the result is “if.”

But we need the full power of the funk, because if `b` produces, say, `7`, all kinds of weirdness will result. We’d really like `6` to just crash if the test product is not a boolean. How can we accomplish this? This is an excellent way to prove to yourself that you understand Nock: figure out what the real `6` does. Or you could just agree that `6` is “if,” and move on.

(It’s worth noting that in practical, compiler-generated Nock, we never do anything as funky as these `6` macro internals. There’s no reason we couldn’t build formulas at runtime, but we have no reason to and we don’t - except when actually metaprogramming. As in most languages, normally code is code and data is data.)


"""
OP_FAS = 0
OP_CON = 1
OP_TAR = 2
OP_WUT = 3
OP_LUS = 4
OP_TIS = 5
OP_IF  = 6
OP_H07 = 7
OP_H08 = 8
OP_H09 = 9
OP_H10 = 10


def _tar(noun):
    """*[a, b] -- Reduce a Nock expression.

    ## 19 ::    *[a [b c] d]      [*[a b c] *[a d]]
    >>> tar((42, ((4, 0, 1), (3, 0, 1))))
    (43, 1)

    ## 21 ::    *[a 0 b]          /[b a]
    >>> tar((2, 0, 1))
    2
    >>> tar((((4, 5), (6, 14, 15)), (0, 7)))
    (14, 15)

    ## 22 ::    *[a 1 b]          b
    >>> tar((42, 1, 5))
    5
    >>> tar((42, (1, 153, 218)))
    (153, 218)

    ## 23 ::    *[a 2 b c]        *[*[a b] *[a c]]
    >>> tar((77, (2, (1, 42), (1, 1, 153, 218))))
    (153, 218)

    ## 24 ::    *[a 3 b]          ?*[a b]
    ## 25 ::    *[a 4 b]          +*[a b]
    ## 26 ::    *[a 5 b]          =*[a b]
    >>> tar((57, (0, 1)))
    57
    >>> tar(((132, 19), (0, 3)))
    19
    >>> tar(((42, 43), (3, 0, 1)))
    0
    >>> tar((42, (3, 0, 1)))
    1
    >>> tar((57, (4, 0, 1)))
    58
    >>> tar((((57, 57), (5, 0, 1))))
    0
    >>> tar((((57, 58), (5, 0, 1))))
    1

    ## 28 ::    *[a 6 b c d]      *[a 2 [0 1] 2 [1 c d] [1 0] 2 [1 2 3] [1 0] 4 4 b]
    >>> tar((42, (6, (1, 0), (4, 0, 1), (1, 233))))
    43
    >>> tar((42, (6, (1, 1), (4, 0, 1), (1, 233))))
    233

    ## 29 ::    *[a 7 b c]        *[a 2 b 1 c]
    >>> tar((42, (7, (4, 0, 1), (4, 0, 1))))
    44

    ## 30 ::    *[a 8 b c]        *[a 7 [[7 [0 1] b] 0 1] c]
    >>> tar((42, (8, (4, 0, 1), (0, 1))))
    (43, 42)
    >>> tar((42, (8, (4, 0, 1), (4, 0, 3))))
    43

    ## 33 ::    *[a 10 b c]       *[a c]
    >>> tar(((132, 19), (10, 37, (4, 0, 3))))
    20
    """
    noun = _t(*noun)
    # Let's use `_fas` to carve up the noun, for practice.
    subj = _fas((2, noun))  # noun[0]
    op = _fas((6, noun))  # noun[1][0]
    obj = _fas((7, noun))  # noun[1][1]
    with _indent():
        if _wut(op) == YES:
            _d("<- 19 ::    *[a [b c] d]      [*[a b c] *[a d]]")
            with _indent():
                return (tar((subj, op)), tar((subj, obj)))
        else:
            if op == OP_FAS:
                _d("<- 21 ::    *[a 0 b]          /[b a]")
                return fas((obj, subj))

            elif op == OP_CON:
                _d("<- 22 ::    *[a 1 b]          b")
                return obj

            elif op == OP_TAR:
                _d("<- 23 ::    *[a 2 b c]        *[*[a b] *[a c]]")
                b = _fas((2, obj))
                c = _fas((3, obj))
                with _indent():
                    return tar((tar((subj, b)), tar((subj, c))))

            elif op == OP_WUT:
                _d("<- 24 ::    *[a 3 b]          ?*[a b]")
                return wut(tar((subj, obj)))

            elif op == OP_LUS:
                _d("<- 25 ::    *[a 4 b]          +*[a b]")
                return lus(tar((subj, obj)))

            elif op == OP_TIS:
                _d("<- 26 ::    *[a 5 b]          =*[a b]")
                return tis(tar((subj, obj)))

            elif op == OP_IF:
                _d("<- 28 ::    *[a 6 b c d]      *[a 2 [0 1] 2 [1 c d] [1 0] 2 [1 2 3] [1 0] 4 4 b]")
                a = subj
                b = _fas((2, obj))
                c = _fas((6, obj))
                d = _fas((7, obj))
                with _indent():
                    return tar((a, 2, (0, 1), 2, (1, c, d), (1, 0), 2, (1, 2, 3), (1, 0), 4, 4, b))

            elif op == OP_H07:
                _d("<- 29 ::    *[a 7 b c]        *[a 2 b 1 c]")
                b = _fas((2, obj))
                c = _fas((3, obj))
                with _indent():
                    return tar((subj, 2, b, 1, c))

            elif op == OP_H08:
                _d("<- 30 ::    *[a 8 b c]        *[a 7 [[7 [0 1] b] 0 1] c]")
                b = _fas((2, obj))
                c = _fas((3, obj))
                with _indent():
                    return tar((subj, 7, ((7, (0, 1), b), 0, 1), c))

            elif op == OP_H09:
                _d("<- 31 ::    *[a 9 b c]        *[a 7 c 2 [0 1] 0 b]")
                b = _fas((2, obj))
                c = _fas((3, obj))
                with _indent():
                    return tar((subj, 7, c, 2, (0, 1), 0, b))

            elif op == OP_H10:
                hint = _fas((2, obj))
                if _wut(hint) == YES:
                    _d("<- 32 ::    *[a 10 [b c] d]   *[a 8 c 7 [0 3] d]")
                    c = _fas((2, hint))
                    with _indent():
                        return tar((subj, 8, c, 7, (0, 3), obj))
                else:
                    _d("<- 33 ::    *[a 10 b c]       *[a c]")
                    c = _fas((3, obj))
                    with _indent():
                        return tar((subj, c))


### HELPERS, because WE NEED HELP.
##################################
def _r(noun):
    """Return a Nock-like repr() of the given noun.

    >>> _r((42, 0, 1))
    '[42 0 1]'
    """
    if isinstance(noun, int):
        return repr(noun)
    else:
        return '[%s]' % ' '.join(_r(i) for i in noun)


DEBUG_LEVEL = 0


@contextlib.contextmanager
def _indent():
    """Context manager to raise and lower the debug output indentation level.
    """
    global DEBUG_LEVEL
    DEBUG_LEVEL += 1
    try:
        yield
    finally:
        DEBUG_LEVEL -= 1


def _d(*args):
    """Log, at the given indentation level, the given logging arguments.
    """
    level = DEBUG_LEVEL * ' '
    a = level + args[0]
    return logger.debug(a, *args[1:])


def _public(original_func, formatter):
    """Create a public interface w/ debug warts.
    """
    def wrapper(noun):
        _d(formatter, _r(noun))
        result = original_func(noun)
        with _indent():
            _d(_r(result))
        return result
    wrapper.__name__ = original_func.__name__.replace('_', '')
    wrapper.__doc__ = original_func.__doc__
    return wrapper

### Public interface for Nock implementation functions.
#######################################################
wut = _public(_wut, '?%s')
lus = _public(_lus, '+%s')
tis = _public(_tis, '=%s')
fas = _public(_fas, '/%s')
tar = _public(_tar, '*%s')


def nock(n):
    """Reduce a Nock expression.

    >>> nock((2, 0, 1))
    2
    >>> nock('[2 0 1]')
    2
    >>> nock('*[2 0 1]')
    2
    """
    expr = n
    if isinstance(n, basestring):
        expr = parse(n)
        if n.startswith('*'):
            return expr

    return tar(expr)


def debug(on=True):
    """Switch debug mode on.

    This logs each step of a Nock reduction, with indentation, so that you can
    kinda sorta tell what the heck is going on.
    """
    root = logging.getLogger()
    if on:
        if not root.handlers:
            logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(DEFAULT_LEVEL)


### The PARSER
##################
TOKENS_CP = re.compile(r'\[|\]|[0-9]+|[*?=/+]')
NUMBERS = set('0123456789')
OPS = {
    '/': fas,
    '+': lus,
    '*': tar,
    '=': tis,
    '?': wut,
}


def _construct(tk_iter, token):
    """Construct and reduce Nock sub-expressions.
    """
    if token == '[':
        out = []
        token = tk_iter.next()
        while token != ']':
            out.append(_construct(tk_iter, token))
            token = tk_iter.next()

        return tuple(out)
    if token in OPS:
        return OPS[token](_construct(tk_iter, tk_iter.next()))
    elif token[0] in NUMBERS:
        return int(token)

    raise SyntaxError("Malformed Nock expression.")


def parse(s):
    """Nock parser.

    Based on effbot's `iterator-based parser`_.

    .. _iterator-based parser: http://effbot.org/zone/simple-iterator-parser.htm
    """
    tokens = iter(TOKENS_CP.findall(s))
    return _construct(tokens, tokens.next())


def main():
    import sys
    import readline
    readline.parse_and_bind('tab: complete')
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    print "Welcome to Nock! (`:q` or ^D to quit; `:debug on` to enter debug mode)"
    print "    (If you're totally confused, read http://www.urbit.org/2013/08/22/Chapter-2-nock.html)"
    print
    try:
        DEBUG = False
        while True:
            line = raw_input('-> ').strip()
            if not line:
                continue
            elif line == ':q':
                break

            elif line.startswith(':debug'):
                if line.endswith('off'):
                    DEBUG = False
                elif line.endswith('on'):
                    DEBUG = True
                else:
                    DEBUG = not DEBUG

                debug()
            else:
                print _r(parse(line))
                print
    except EOFError:
        pass

    print "Good-bye!"
    print
    sys.exit()

if __name__ == "__main__":
    main()
