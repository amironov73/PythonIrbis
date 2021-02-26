===========
PythonIrbis
===========

``PythonIrbis`` package is universal client software for IRBIS64 library
automation system (`ManagedIrbis <https://github.com/amironov73/ManagedIrbis>`_
package ported from C# to Python 3). Available on `PyPi <https://pypi.org/project/irbis>`_.

Supported environments
======================

``PythonIrbis`` currently supports Python 3.6 and 3.7 on 32-bit and 64-bit Windows, Linux, Mac OS X and IRBIS64 server version 2014 or later.

Sample program
==============

.. code-block:: python

  import irbis

  # Connect to the server
  client = irbis.Connection()
  client.parse_connection_string('host=127.0.0.1;database=IBIS;' +
      'user=librarian;password=secret;')
  client.connect()

  if not client.connected:
      print("Can't connect")
      exit(1)

  # Search for books written by Byron
  found = client.search('"A=Byron$"')
  print(f'Records found: {len(found)}')

  # Take first 10 records
  for mfn in found[:10]:
      # Read the record from the server
      record = client.read_record(mfn)

      # Extract the field and subfield from the record
      title = record.fm(200, 'a')
      print(f'Title: {title}')

      # Format the record by the server
      description = client.format_record(irbis.BRIEF, mfn)
      print(f'Description: {description}')

      print()  # Print empty line

  # Disconnect from the server
  client.disconnect()

Links
=====

* `Builds on AppVeyor <https://ci.appveyor.com/project/AlexeyMironov/pythonirbis/>`_;

Build status
============

|Issues| |Release| |Build| |FOSSA Status| |GitHub Action|

.. |Issues| image:: https://img.shields.io/github/issues/amironov73/PythonIrbis.svg
    :target: https://github.com/amironov73/PythonIrbis/issues
    :alt: Issues

.. |Release| image:: https://img.shields.io/github/release/amironov73/PythonIrbis.svg
    :target: https://github.com/amironov73/PythonIrbis/releases
    :alt: Release

.. |Build| image:: https://img.shields.io/appveyor/ci/AlexeyMironov/pythonirbis.svg
    :target: https://ci.appveyor.com/project/AlexeyMironov/pythonirbis/
    :alt: Build

.. |FOSSA Status| image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Famironov73%2FPythonIrbis.svg?type=shield
    :target: https://app.fossa.io/projects/git%2Bgithub.com%2Famironov73%2FPythonIrbis?ref=badge_shield
    :alt: FOSSA Status

.. |GitHub Action| image:: https://github.com/amironov73/PythonIrbis/workflows/Python%20package/badge.svg
    :target: https://github.com/amironov73/PythonIrbis/actions
    :alt: GitHub Action

License
=======

.. image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Famironov73%2FPythonIrbis.svg?type=large
    :alt: FOSSA Status
    :target: https://app.fossa.io/projects/git%2Bgithub.com%2Famironov73%2FPythonIrbis?ref=badge_large

Documentation (in russian)
==========================

* https://pythonirbis.readthedocs.io/
