# HPE 3PAR Software Development Kit for Python

This is a Client library that can talk to the HPE 3PAR Storage array. The 3PAR storage array has a REST web service interface and a command line interface. This client library implements a simple interface for talking with either interface, as needed. The python Requests library is used to communicate with the REST interface. The python paramiko library is used to communicate with the command line interface over an SSH connection.

### Requirements
This branch requires 3.1.3 version MU1 or later of the 3PAR firmware.

### Capabilities
* Create Volume
* Delete Volume
* Get all Volumes
* Get a Volume
* Modify a Volume
* Copy a Volume
* Create a Volume Snapshot
* Create CPG
* Delete CPG
* Get all CPGs
* Get a CPG
* Get a CPG's Available Space
* Create a VLUN
* Delete a VLUN
* Get all VLUNs
* Get a VLUN
* Create a Host
* Delete a Host
* Get all Hosts
* Get a Host
* Get VLUNs for a Host
* Find a Host
* Find a Host Set for a Host
* Get all Host Sets
* Get a Host Set
* Create a Host Set
* Delete a Host Set
* Modify a Host Set
* Get all Ports
* Get iSCSI Ports
* Get FC Ports
* Get IP Ports
* Set Volume Metadata
* Get Volume Metadata
* Get All Volume Metadata
* Find Volume Metadata
* Remove Volume Metadata
* Create a Volume Set
* Delete a Volume Set
* Modify a Volume Set
* Get a Volume Set
* Get all Volume Sets
* Find one Volume Set containing a specified Volume
* Find all Volume Sets containing a specified Volume
* Create a QOS Rule
* Modify a QOS Rule
* Delete a QOS Rule
* Set a QOS Rule
* Query a QOS Rule
* Query all QOS Rules
* Get a Task
* Get all Tasks
* Get a Patch
* Get all Patches
* Get WSAPI Version
* Get WSAPI Configuration Info
* Get Storage System Info
* Get Overall System Capacity
* Stop Online Physical Copy
* Query Online Physical Copy Status
* Stop Offline Physical Copy
* Query Remote Copy Info
* Query a Remote Copy Group
* Query all Remote Copy Groups
* Create a Remote Copy Group
* Delete a Remote Copy Group
* Modify a Remote Copy Group
* Add a Volume to a Remote Copy Group
* Remove a Volume from a Remote Copy Group
* Start Remote Copy on a Remote Copy Group
* Stop Remote Copy on a Remote Copy Group
* Synchronize a Remote Copy Group
* Recover a Remote Copy Group from a Disaster
* Enable/Disable Config Mirroring on a Remote Copy Target
* Promote Virtual Copy

### Installation
 To install:
```bash
$ sudo pip install .
```
Unit Tests
To run all unit tests:
```bash
$ tox -e py27
```
To run a specific test:
```bash
$ tox -e py27 -- test/file.py:class_name.test_method_name
```
To run all unit tests with code coverage:
```bash
$ tox -e cover
```
The output of the coverage tests will be placed into the coverage dir.

### Folders
* docs -- contains the documentation.
* hpe3par_sdk -- the actual client.py library
* test -- unit tests
### Documentation
To build the documentation:
```bash
$ tox -e docs
```
To view the built documentation point your browser to:

docs/html/index.html
### Running Simulators
The unit tests should automatically start/stop the simulators. To start them manually use the following commands. To stop them, use 'kill'. Starting them manually before running unit tests also allows you to watch the debug output.

WSAPI:
```bash
$ python test/HPE3ParMockServer_flask.py -port 5001 -user <USERNAME> -password <PASSWORD> -debug
```
SSH:
```bash
$ python test/HPE3ParMockServer_ssh.py [port]
```
