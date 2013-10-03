=====
Nock!
=====

If you don't know what Nock is, you better start `here`_. It'll take you a while. Don't worry. We'll still be here when you get back.

.. _here: http://www.urbit.org

Welcome back! Now that you know what Nock is... have you written a Nock parser, and you still don't understand Nock? This module is for you. Not only is this a fully [1]_ functional [2]_ Nock environment, it's a Nock environment that will explain what the heck is going on.

The module is written in a literate style (cribbing generously from urbit.org). We encourage a `close reading`_. While you're reading, we also recommend playing along at home::

    In [1]: from nock import *

    In [2]: debug()

    In [3]: tar((42, (4, 0, 1)))
    DEBUG:nock:-> *[42 [4 [0 1]]]
    DEBUG:nock:    <- 25 ::    *[a 4 b]          +*[a b]
    DEBUG:nock:    -> *[42 [0 1]]
    DEBUG:nock:        <- 21 ::    *[a 0 b]          /[b a]
    DEBUG:nock:        /[1 42]
    DEBUG:nock:    +42
    Out[3]: 43


.. _close reading: https://github.com/eykd/nock/blob/master/nock.py

Unfortunately, there's no parser yet, so you have to translate into function calls and tuples, but we use true names for all the operators, so we only help you sink deeper into the water. Soon enough, you won't even realize you're breathing it.


Credits
=======

Thanks to James Tauber, for his original `pynock`_. This would have taken a lot longer without that. And of course, thanks to `C. Guy Yarvin`_, for his methodical madness.

.. _pynock: https://github.com/jtauber/pynock/
.. _C. Guy Yarvin: http://moronlab.blogspot.com

---------------

.. [1] For some definition of "fully".
.. [2] Get it? *Get it?*

