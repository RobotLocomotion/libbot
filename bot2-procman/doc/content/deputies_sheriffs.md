Deputies and Sheriffs {#procman_deputies_sheriffs}
=====================

This page explains the relationship between deputies and sheriffs, and provides
an overview of the communication protocol.

Deputy - bot-procman-deputy
------

A procman deputy is a single process that directly controls user-specified
processes.  The deputy is responsible for starting commands, stopping commands,
and intercepting and transmitting their output (both standard out and standard
error).  It also reports information on how much CPU and memory each command is
using, and can automatically restart commands when they terminate (if
requested).

The deputy is essentially a daemon process that manages other commands.  It is
not interactive, does not have a GUI, and simply carries out orders that it
receives from a sheriff.

Sheriff - bot-procman-sheriff
-------

The procman sheriff is a process that controls the deputies.  The sheriff forms
a global view of all deputies and their commands.  The sheriff sends commands
to the deputies, and specifies which commands a deputy should be managing, and
the desired state of those commands.

The sheriff has an interactive GUI through which a user can modify commands and
their desired statuses.  It also has a scripting facility that can be useful
for starting multiple commands at once, sequencing a startup procedure, or
running simple scripts in general.

The sheriff can also be run from the command line without a GUI.

\image html procman-sheriff-screenshot.png "bot-procman-sheriff screenshot"

### Observer mode

A sheriff can be switched to observer mode, where it stops transmitting
commands, and simply displays the state of the deputies.  Observer mode is
useful in situations where you want to simply observe the state of a running
system.  Examples of this include situations where the active sheriff is
running without a GUI, and also when replaying an LCM log file that contains
deputy status message (using the LCM log playback tools).

Communication
-------------

Sheriffs and deputies communicat by transmitting LCM messages to each other.
Deputies periodically (1 Hz) transmit their current status, which includes:
- A listing of each command managed by the deputy and. For each command:
  - Whether the command is running
  - The OS-assigned process ID of the command, if it's running
  - How much CPU and memory are used by the command
  - Which group the command is in

In addition to the deputy state, each deputy also captures the standard output
and standard error for each running command, and transmits the output over LCM.

Sheriffs transmit the desired state for each deputy.  For each deputy, the
sheriff periodically (1 Hz) transmits a message containing:
- A listing of all commands the deputy _should_ be managing and the desired
state for each command:
  - If the command should be running, stopped, or restarted
  - The program to run, command line arguments, and environment variables.
  - Which group the command should be in.
  - If the command should be automatically restarted if/when it terminates.

The communications protocol is stateless by design:  every message transmitted
from a sheriff to the deputy contains the entire desired state of the deputy.
Similarly, every message transmitted by a deputy contains its entire internal
state.  This stateless protocol has a few key features:
- The entire system is robust to communication dropouts.
If a deputy stops receiving messages from the sheriff, the deputy simply
continues carrying out its last orders.
- When the sheriff starts up, it seamlessly picks up the entire state of the
system as it receives updates from each deputy.  Deputies are
unaffected by a sheriff starting up until the sheriff begins transmitting
orders.
- A sheriff in observer mode (see above) can pick up the state of the system
simply by receiving deputy messages and not transmitting anything.
