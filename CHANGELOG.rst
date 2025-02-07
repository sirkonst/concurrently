Changelog
=========

2.1
---

* Add support python 3.13

2.0
---

* Add support python 3.11 and 3.12
* Drop support python 3.5 and 3.6
* Use tuples for AbstractWaiter.exceptions() instead of list
* Fix example
* Migrate pylava -> pylama

1.2
---

* Add support python 3.10
* Fix example

1.1
---

* Add support python 3.9

1.0
---

* Add support python 3.8

0.12
----

* Add support python 3.7
* Fix tests and build

0.10.0
------

* beta release
* Ensure that decorated function for  AsyncIOThreadEngine is not  coroutine
* Ensure that decorated function for  AsyncIOEngine is  coroutine
* added Sphinx documentation

0.8.0
-----

* Unification tests
* Lazy import for engines
* Add new GeventEngine

0.7.0
-----

* Removed AsyncIOExecutorEngine and returned AsyncIOThreadEngine, removed ThreadPoolEngine
* Fix deploy

0.6.0
-----

* Refact KillableThread
* New option fail_hard for Waiter
* Automatic deploy by travis-ci

0.5.0
-----

* Waiter raises UnhandledExceptions until specifying suppress_exceptions=True

0.4.0
-----

* Support for specifying custom pool in ThreadPoolEngine

0.3.0
-----

* AsyncIOThreadEngine replaced by AsyncIOExecutorEngine

0.2.0
-----

* Public version
