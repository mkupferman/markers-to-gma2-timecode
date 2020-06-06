# midi2gma2tc

MIDI to GrandMA2 Timecode

This helps automate the process of creating a GrandMA2 timecode object with a sequence track, based on event markers in a MIDI file.

Often it is deisrable to create markers in a digital audio workstation (DAW) against an audio file, and transfer that to GrandMA2 as a skeleton to program timecoded cues. Many DAWs (such as ProTools) can export these markers into MIDI, which this script can read.

## Requirements

-   A UNIX-like environemnt, such as:
    -   Linux
    -   macOS X
    -   Windows running Git Bash
-   Python (3.5 or greater)
    -   virtualenv support preferred
-   GrandMA2 software (tested on 3.9)
-   A MIDI file with markers written within

## Installation

[Here is a video](https://www.youtube.com/watch?v=B-IXtyj8Qxs) demonstrating the installation and usage of this script with ProTools and GrandMA onPC.

    sh build.sh
    # in Linux/macOS/etc:
    source venv/bin/activate

    # in Windows:
    source venv/Scripts/activate

## Usage

    midi2gma2tc [OPTIONS] MIDIFILE TIMECODE_OUT MACRO_OUT
    Options:
      -l, --label TEXT               Label for sequence/executor/timecode in MA2
      -s, --sequence-number INTEGER  MA2 sequence pool number to overwrite
      -t, --timecode-number INTEGER  MA2 timecode pool number to overwrite
      -p, --exec-page INTEGER        MA2 executor page to store executor
      -e, --exec-number INTEGER      MA2 executor number to overwrite
      -f, --frame-rate [24|25|30]    Timecode framerate (will override value from MIDI file)

## Examples

    export GMADATA="/c/programdata/ma lightning technologies/grandma/gma_V_3.9"

    midi2gma2tc --label "Happy Birthday" \
        --sequence-number 101 \
        --exec-page 1 \
        --exec-number 101 \
        --timecode-number 1 \
        --frame-rate 30 \
        from_protools.mid \
        "$GMADATA/importexport/happybirthday_tc.xml" \
        "$GMADATA/macros/happybirthday.xml"

This will create 2 XML files in the MA2 data directory:

1.  An XML representation of the timecode
2.  An importable macro to create the sequence, executor, and timecode.

At the command line in GrandMA2, assuming macro slot 101 is free:

    import happybirthday_tc.xml at macro 101
    go macro 101

This macro will:

1.  Create (or overwrite) sequence 101 with cues based on the MIDI markers
2.  Create an executor at 1.101 with sequence 101 assigned to it
3.  Import the timecode data into timecode 1 (overwriting)
