import os
import sys
import logging
import logging.handlers
import re
import subprocess
from gpiozero import Button
import signal
from signal import pause
import psutil

class PinConflict(Exception):
    def __init__(self, conflicting_pin, *video_files):
        # Call the base class constructor with the parameters it needs
        super(PinConflict, self).__init__("GPIO{} ist mit mehreren Videos belegt: {}".format(conflicting_pin, video_files))

        # Now for your custom code...
        self.pin = conflicting_pin
        self.video_files = video_files


video_name_regex = re.compile(r'^(?P<pin>\d\d)_.*$')
video_path = '/usr/local/share/rpi-video-player/'
usb_mountpoint = '/media/usb/'

class VideoPlayer(object):
    def __init__(self):
        self.omxplayer = None

    def play(self, video):
        log.info('Play {}'.format(os.path.basename(video)))
        self.stop()
        self.omxplayer = subprocess.Popen(['omxplayer', '--no-osd', video],
                                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
        log.debug('Started omxplayer')

    def stop(self):
        if self.omxplayer:
            parent = psutil.Process(self.omxplayer.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            self.omxplayer.wait()

    def rewind(self):
        self.omxplayer.write(b'i')
        self.omxplayer.flush()


def find_videos():
    videos = {}
    for s in os.listdir(video_path):
        log.debug('Datei gefunden: {}'.format(s))
        m = video_name_regex.match(s)
        if m:
            pin = int(m.group('pin'))
            if pin not in videos:
                videos[pin] = os.path.join(video_path, s)
            else:
                raise PinConflict(pin, s, os.path.basename(videos[pin]))
    return videos


def main():
    if os.path.isdir(usb_mountpoint):
        if len(os.listdir(usb_mountpoint)) > 0:
            log.info('USB Stick wurde erkannt! Kopiere Daten...')
            subprocess.call(['rsync', '-av', '--delete', usb_mountpoint, video_path])
            log.info('Dateien wurden kopiert. USB Stick kann jetzt entfernt werden.')

    log.debug("Video Player Dienst wurde gestartet")
    video_player = VideoPlayer()
    try:
        videos = find_videos()
        buttons = []

        for pin, video in videos.items():
            button = Button(pin)
            button.when_pressed = (lambda v: (lambda: video_player.play(v)))(video)
            buttons.append(button)
            log.debug('Video file "{}" on GPIO{}'.format(os.path.basename(video), pin))
        pause()
    except PinConflict as e:
        log.critical(str(e))
        log.critical("Bitte entfernen Sie alle bis auf ein Video pro Pin und starten Sie den Raspberry pi neu.")
    finally:
        video_player.stop()



if __name__ == '__main__':
    # configure logging
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    log.addHandler(handler)
    log.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))

    main()
