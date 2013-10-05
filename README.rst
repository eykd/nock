=====
Nock!
=====

If you don't know what Nock is, you had better start `here`_. It'll take you a while. Don't worry. We'll still be here when you get back.

.. _here: http://www.urbit.org

Welcome back! Now that you know what Nock is... have you written a Nock parser, and you still don't understand Nock? This module is for you. Not only is this a fully [1]_ functional [2]_ Nock environment, it's a Nock environment that will explain what the heck is going on.

The module is written in a literate style (cribbing generously from urbit.org). We encourage a `close reading`_. While you're reading, we also recommend playing along at home::

    In [1]: from nock import *

    In [2]: debug()

    In [3]: tar((42, (4, 0, 1)))
		DEBUG:nock:*[42 [4 0 1]]
		DEBUG:nock:    <- 25 ::    *[a 4 b]          +*[a b]
		DEBUG:nock:    *[42 [0 1]]
		DEBUG:nock:        <- 21 ::    *[a 0 b]          /[b a]
		DEBUG:nock:        /[1 42]
		DEBUG:nock:            42
		DEBUG:nock:        42
		DEBUG:nock:    +42
		DEBUG:nock:        43
		DEBUG:nock:    43
    Out[3]: 43

Or better yet::

    In [4]: tar((42, (6, (1, 0), (4, 0, 1), (1, 233))))
		DEBUG:nock:*[42 [6 [1 0] [4 0 1] [1 233]]]
		DEBUG:nock:    <- 28 ::    *[a 6 b c d]      *[a 2 [0 1] 2 [1 c d] [1 0] 2 [1 2 3] [1 0] 4 4 b]
		DEBUG:nock:        *[42 2 [0 1] 2 [1 [4 [0 1]] [1 233]] [1 0] 2 [1 2 3] [1 0] 4 4 [1 0]]
		DEBUG:nock:            <- 23 ::    *[a 2 b c]        *[*[a b] *[a c]]
		DEBUG:nock:                *[42 [0 1]]
		DEBUG:nock:                    <- 21 ::    *[a 0 b]          /[b a]
		DEBUG:nock:                    /[1 42]
		DEBUG:nock:                        42
		DEBUG:nock:                    42
		DEBUG:nock:                *[42 [2 [[1 [[4 [0 1]] [1 233]]] [[1 0] [2 [[1 [2 3]] [[1 0] [4 [4 [1 0]]]]]]]]]]
		DEBUG:nock:                    <- 23 ::    *[a 2 b c]        *[*[a b] *[a c]]
		DEBUG:nock:                        *[42 [1 [[4 [0 1]] [1 233]]]]
		DEBUG:nock:                            <- 22 ::    *[a 1 b]          b
		DEBUG:nock:                            [[4 [0 1]] [1 233]]
		DEBUG:nock:                        *[42 [[1 0] [2 [[1 [2 3]] [[1 0] [4 [4 [1 0]]]]]]]]
		DEBUG:nock:                            <- 19 ::    *[a [b c] d]      [*[a b c] *[a d]]
		DEBUG:nock:                                *[42 [1 0]]
		DEBUG:nock:                                    <- 22 ::    *[a 1 b]          b
		DEBUG:nock:                                    0
		DEBUG:nock:                                *[42 [2 [[1 [2 3]] [[1 0] [4 [4 [1 0]]]]]]]
		DEBUG:nock:                                    <- 23 ::    *[a 2 b c]        *[*[a b] *[a c]]
		DEBUG:nock:                                        *[42 [1 [2 3]]]
		DEBUG:nock:                                            <- 22 ::    *[a 1 b]          b
		DEBUG:nock:                                            [2 3]
		DEBUG:nock:                                        *[42 [[1 0] [4 [4 [1 0]]]]]
		DEBUG:nock:                                            <- 19 ::    *[a [b c] d]      [*[a b c] *[a d]]
		DEBUG:nock:                                                *[42 [1 0]]
		DEBUG:nock:                                                    <- 22 ::    *[a 1 b]          b
		DEBUG:nock:                                                    0
		DEBUG:nock:                                                *[42 [4 [4 [1 0]]]]
		DEBUG:nock:                                                    <- 25 ::    *[a 4 b]          +*[a b]
		DEBUG:nock:                                                    *[42 [4 [1 0]]]
		DEBUG:nock:                                                        <- 25 ::    *[a 4 b]          +*[a b]
		DEBUG:nock:                                                        *[42 [1 0]]
		DEBUG:nock:                                                            <- 22 ::    *[a 1 b]          b
		DEBUG:nock:                                                            0
		DEBUG:nock:                                                        +0
		DEBUG:nock:                                                            1
		DEBUG:nock:                                                        1
		DEBUG:nock:                                                    +1
		DEBUG:nock:                                                        2
		DEBUG:nock:                                                    2
		DEBUG:nock:                                            [0 2]
		DEBUG:nock:                                        *[[2 3] [0 2]]
		DEBUG:nock:                                            <- 21 ::    *[a 0 b]          /[b a]
		DEBUG:nock:                                            /[2 [2 3]]
		DEBUG:nock:                                                2
		DEBUG:nock:                                            2
		DEBUG:nock:                                    2
		DEBUG:nock:                            [0 2]
		DEBUG:nock:                        *[[[4 [0 1]] [1 233]] [0 2]]
		DEBUG:nock:                            <- 21 ::    *[a 0 b]          /[b a]
		DEBUG:nock:                            /[2 [[4 [0 1]] [1 233]]]
		DEBUG:nock:                                [4 [0 1]]
		DEBUG:nock:                            [4 [0 1]]
		DEBUG:nock:                    [4 [0 1]]
		DEBUG:nock:                *[42 [4 [0 1]]]
		DEBUG:nock:                    <- 25 ::    *[a 4 b]          +*[a b]
		DEBUG:nock:                    *[42 [0 1]]
		DEBUG:nock:                        <- 21 ::    *[a 0 b]          /[b a]
		DEBUG:nock:                        /[1 42]
		DEBUG:nock:                            42
		DEBUG:nock:                        42
		DEBUG:nock:                    +42
		DEBUG:nock:                        43
		DEBUG:nock:                    43
		DEBUG:nock:            43
		DEBUG:nock:    43
    Out[4]: 43

Horrifying, innit? Welcome to life in the offworld colonies. The air gets installed next week.

.. _close reading: https://github.com/eykd/nock/blob/master/nock.py

Unfortunately, there's no parser yet, so you have to translate that lovely Nock syntax into verbose Python function calls and tuples, but we use true names for all the operators, so we only help you sink deeper into the water. Is that really water? Either way, soon enough, you won't even realize you're breathing it.

Tests
=====

Did we mention we have tests? Bushels and bushels of glorious doctests. Well, for everything except lines 31 and 32. We have no idea what those are about, but we're sure they're just fine.

To run the tests, install nose_ and run it with::

    nosetests --with-doctest

.. _nose: https://pypi.python.org/pypi/nose/

Contributing
============

Is something bothering you? Join the club. Join the club and `open an issue`_, that is. Do you have a way to make this better? Do you happen to have a Nock parser burning a hole in your back pocket? DO YOU UNDERSTAND WHAT LINES 31 AND 32 MEAN, AND CAN YOU WRITE TESTS TO PROVE IT?! Open a *pull request*.

.. _open an issue: https://github.com/eykd/nock/issues

Credits
=======

Thanks to James Tauber, for his original `pynock`_. This would have taken a lot longer without that. And of course, thanks to `C. Guy Yarvin`_, for his methodical madness.

.. _pynock: https://github.com/jtauber/pynock/
.. _C. Guy Yarvin: http://moronlab.blogspot.com

---------------

.. [1] For some definition of "fully".
.. [2] Get it? *Get it?*

