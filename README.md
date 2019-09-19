# PythonIrbis

`PythonIrbis` package is just [ManagedIrbis](https://github.com/amironov73/ManagedIrbis) package ported from C# to Python 3

### Supported environments

`PythonIrbis` currently supports Python 3.6 and 3.7 on 32-bit and 64-bit Windows, Linux, Mac OS X and IRBIS64 server version 2014 or later.

### Sample program

```python
import irbis

# Connect to the server
client = irbis.Connection()
client.parse_connection_string('host=127.0.0.1;database=IBIS;' + \
    'user=librarian;password=secret;')
client.connect()

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
```

### Links

- [Builds on AppVeyor](https://ci.appveyor.com/project/AlexeyMironov/pythonirbis/);

### Build status

[![Issues](https://img.shields.io/github/issues/amironov73/PythonIrbis.svg)](https://github.com/amironov73/PythonIrbis/issues)
[![Release](https://img.shields.io/github/release/amironov73/PythonIrbis.svg)](https://github.com/amironov73/PythonIrbis/releases)
[![Build status](https://img.shields.io/appveyor/ci/AlexeyMironov/pythonirbis.svg)](https://ci.appveyor.com/project/AlexeyMironov/pythonirbis/)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Famironov73%2FPythonIrbis.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Famironov73%2FPythonIrbis?ref=badge_shield)
[![GitHub Action](https://github.com/amironov73/PythonIrbis/workflows/Python%20package/badge.svg)](https://github.com/amironov73/PythonIrbis/actions)

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Famironov73%2FPythonIrbis.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Famironov73%2FPythonIrbis?ref=badge_large)

#### Documentation (in russian)

* [**Introduction**](docs/chapter1.md)
* [**Connection class**](docs/chapter2.md)
* [**MarcRecord, RecordField and SubField classes**](docs/chapter3.md)
* [**Other classes and functions**](docs/chapter4.md)
* [**Request builder**](docs/chapter5.md)
* [**Import/export**](docs/chapter6.md)

