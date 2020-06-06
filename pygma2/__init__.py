#!/usr/bin/env python

import mido

import xml.etree.ElementTree as ET
ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
ET.register_namespace('', "http://schemas.malighting.de/grandma2/xml/MA")


def ma2LabelSanitize(string):
    """ Remove characters that could make labeling difficult """
    return string.replace('"', '')


def sec2frames(seconds, frameRate):
    return int(round(seconds * frameRate, 0))


class TempoMarker:
    """ Tempo indicator from MIDI source file """

    def __init__(self, time, tempo):
        self.time = time
        self.tempo = tempo

    def __repr__(self):
        return "TempoMarker(time=%s, tempo=%s)\n" % (self.time, self.tempo)


class CueMarker:
    """ Marker from MIDI source file """

    def __init__(self, time, label):
        self.time = time
        self.label = label

    def __repr__(self):
        return "CueMarker(time=%s, label=%s)\n" % (self.time, self.label)


class MidiFile:
    def __init__(self, filepath):
        self.tempos = []
        self.cues = []
        self.frameRate = 30  # default

        m = mido.MidiFile(filepath)
        self.totalLength = float(m.length)

        timeTrack = float(0)
        for msg in m:
            if hasattr(msg, 'time'):
                # ticks in messages are only deltas
                timeTrack += msg.time

            if msg.type == 'smpte_offset':
                self.frameRate = msg.frame_rate
            elif msg.type == 'set_tempo':
                bpm = int(round(mido.tempo2bpm(msg.tempo), 0))
                self.tempos.append(TempoMarker(timeTrack, bpm))
            elif msg.type == 'marker':
                self.cues.append(CueMarker(timeTrack, msg.text))

    def getCues(self):
        return self.cues

    def getTempos(self):
        return self.tempos

    def getFrameRate(self):
        """ Note: this is not always reflective of what SMPTE/LTC/MTC will be! """
        return self.frameRate

    def getTotalLength(self):
        """ in seconds """
        return self.totalLength


class Macro:
    """ Macro in MA2 """

    def __init__(self, label):
        self.label = label
        self.macroLines = []

    def addLine(self, cmd):
        self.macroLines.append(cmd)

    def toXml(self, filename=None):
        if filename is None:
            pass  # TODO print xml to stdout
        else:
            root = ET.Element('MA')
            root.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
                     'http://schemas.malighting.de/grandma2/xml/MA http://schemas.malighting.de/grandma2/xml/3.9.0/MA.xsd')
            root.set('major_vers', '3')
            root.set('minor_vers', '0')
            root.set('stream_vers', '0')

            maMacro = ET.SubElement(
                root, '{http://schemas.malighting.de/grandma2/xml/MA}Macro')
            maMacro.set('index', '1')
            maMacro.set('name', self.label)

            macroIndex = 0
            for line in self.macroLines:
                macroLine = ET.SubElement(
                    maMacro, '{http://schemas.malighting.de/grandma2/xml/MA}Macroline')
                macroLine.set('index', str(macroIndex))
                macroText = ET.SubElement(
                    macroLine, '{http://schemas.malighting.de/grandma2/xml/MA}text')
                macroText.text = line

                macroIndex += 1

            ET.ElementTree(root).write(
                filename, encoding='utf-8', xml_declaration=True)


class TimecodeSingletrack:
    """ MA2 timecode item with 1 track/subtrack """

    def __init__(self, seqName, seqNum, execPage, execNum, length, frameRate):
        self.seqName = seqName
        self.seqNum = seqNum
        self.execPage = execPage
        self.execNum = execNum
        self.length = length  # in frames
        self.frameRate = frameRate
        self.events = []

    def addCue(self, cueMarker):
        self.events.append(cueMarker)

    def toXml(self, filename=None):
        if filename is None:
            pass  # TODO print xml to stdout
        else:
            root = ET.Element('MA')
            root.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
                     'http://schemas.malighting.de/grandma2/xml/MA http://schemas.malighting.de/grandma2/xml/3.9.0/MA.xsd')
            root.set('major_vers', '3')
            root.set('minor_vers', '0')
            root.set('stream_vers', '0')

            timecode = ET.SubElement(
                root, '{http://schemas.malighting.de/grandma2/xml/MA}Timecode')
            timecode.set('index', '1')
            timecode.set('lenght', str(
                sec2frames(self.length, self.frameRate)))
            timecode.set('slot', 'Link Selected')
            timecode.set('frame_format', '%s FPS' % self.frameRate)
            timecode.set('m_autostart', 'true')

            track = ET.SubElement(
                timecode, '{http://schemas.malighting.de/grandma2/xml/MA}Track')
            track.set('index', '0')
            track.set('active', 'true')

            trackObject = ET.SubElement(
                track, '{http://schemas.malighting.de/grandma2/xml/MA}Object')
            trackObject.set('name', '%s %s.%s' %
                            (self.seqName, self.execPage, self.execNum))
            obj = ET.SubElement(
                trackObject, '{http://schemas.malighting.de/grandma2/xml/MA}No')
            obj.text = '30'
            obj = ET.SubElement(
                trackObject, '{http://schemas.malighting.de/grandma2/xml/MA}No')
            obj.text = '1'
            execPage = ET.SubElement(
                trackObject, '{http://schemas.malighting.de/grandma2/xml/MA}No')
            execPage.text = str(self.execPage)
            execNum = ET.SubElement(
                trackObject, '{http://schemas.malighting.de/grandma2/xml/MA}No')
            execNum.text = str(self.execNum)

            subTrack = ET.SubElement(
                track, '{http://schemas.malighting.de/grandma2/xml/MA}SubTrack')
            subTrack.set('index', '0')

            cueIndex = 0
            for event in self.events:
                if isinstance(event, CueMarker):
                    tcEvent = ET.SubElement(
                        subTrack, '{http://schemas.malighting.de/grandma2/xml/MA}Event')
                    tcEvent.set('index', str(cueIndex))
                    tcEvent.set('command', 'Go')
                    tcEvent.set('pressed', 'true')
                    tcEvent.set('step', str(cueIndex + 1))
                    tcEvent.set('time', str(
                        sec2frames(event.time, self.frameRate)))

                    tcCue = ET.SubElement(
                        tcEvent, '{http://schemas.malighting.de/grandma2/xml/MA}Cue')
                    tcCue.set('name', ma2LabelSanitize(event.label))
                    obj = ET.SubElement(
                        tcCue, '{http://schemas.malighting.de/grandma2/xml/MA}No')
                    obj.text = '1'
                    obj = ET.SubElement(
                        tcCue, '{http://schemas.malighting.de/grandma2/xml/MA}No')
                    obj.text = str(self.seqNum)
                    obj = ET.SubElement(
                        tcCue, '{http://schemas.malighting.de/grandma2/xml/MA}No')
                    obj.text = str(cueIndex + 1)

                    cueIndex += 1

            ET.ElementTree(root).write(
                filename, encoding='utf-8', xml_declaration=True)
