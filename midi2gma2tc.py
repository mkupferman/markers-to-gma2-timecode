#!/usr/bin/env python3

from pygma2 import *
import os
import click


@click.command()
@click.argument('midifile', type=click.Path(exists=True))
@click.argument('timecode-out', type=click.Path())
@click.argument('macro-out', type=click.Path())
@click.option('--label', '-l', default='My Song', help='Label for sequence/executor/timecode in MA2')
@click.option('--sequence-number', '-s', default=101, help='MA2 sequence pool number to overwrite')
@click.option('--timecode-number', '-t', default=1, help='MA2 timecode pool number to overwrite')
@click.option('--exec-page', '-p', default=1, help='MA2 executor page to store executor')
@click.option('--exec-number', '-e', default=101, help='MA2 executor number to overwrite')
@click.option('--frame-rate', '-f', default=None, type=click.Choice(['24', '25', '30']), help='Timecode framerate (will override value from MIDI file)')
def midi2gma2tc(midifile, timecode_out, macro_out, label, sequence_number, timecode_number, exec_page, exec_number, frame_rate):

    midiTrack = MidiFile(midifile)

    # frame rate sanity check
    if frame_rate is not None:
        frameRate = int(frame_rate)  # use override argument
    elif midiTrack.getFrameRate in [24, 25, 30]:
        frameRate = midiTrack.getFrameRate
    else:
        frameRate = 30  # default fallback

    # assemble the timecode object and macro
    timecode = TimecodeSingletrack(
        label, sequence_number, exec_page, exec_number, midiTrack.getTotalLength(), frameRate)
    macro = Macro("Setup TC %s" % ma2LabelSanitize(label))

    cueNum = 1
    for cue in midiTrack.getCues():
        timecode.addCue(cue)
        macro.addLine('store seq %s cue %s "%s" /o /nc' %
                      (sequence_number, cueNum, ma2LabelSanitize(cue.label)))
        cueNum += 1

    macro.addLine('label seq %s "%s"' %
                  (sequence_number, ma2LabelSanitize(label)))
    macro.addLine('assign seq %s at exec %s.%s' %
                  (sequence_number, exec_page, exec_number))
    macro.addLine('sd 1')
    macro.addLine('import "%s" at timecode %s /o /nc' %
                  (ma2LabelSanitize(os.path.basename(timecode_out)), timecode_number))
    macro.addLine('label timecode %s "TC %s"' %
                  (timecode_number, ma2LabelSanitize(label)))

    timecode.toXml(timecode_out)
    macro.toXml(macro_out)
