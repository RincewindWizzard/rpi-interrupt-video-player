import os
import os.path
import sys
import threading
from multiprocessing import Process, Queue

import time
import logging
import logging.handlers
import re
import subprocess
from gpiozero import Button
import signal
from signal import pause
import psutil
import omxplayer
from omxplayer import OMXPlayer

class PinConflict(Exception):
    def __init__(self, conflicting_pin, *video_files):
        # Call the base class constructor with the parameters it needs
        super(PinConflict, self).__init__("GPIO{} ist mit mehreren Videos belegt: {}".format(conflicting_pin, video_files))

        # Now for your custom code...
        self.pin = conflicting_pin
        self.video_files = video_files


video_name_regex = re.compile(r'^(?P<pin>\d\d)_.*$')
video_path = '/usr/local/share/rpi-video-player/'
background_image = os.path.join(video_path, 'background.jpg')
usb_mountpoint = '/media/usb/'
omxplayer_args = ['--no-osd', '-o', 'both', '--loop']


def killall_omxplayer():
    subprocess.call(['killall', 'omxplayer.bin'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def killall_fbi():
    subprocess.call(['killall', 'fbi'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def omxplayer_process(queue):
    try:
        player_num = 0
        last_video = None
        video = True
        while video:
            #log.debug("Warte auf Befehle")
            video = queue.get()
            try:
                # block queue
                queue.put_nowait(True)
            except:
                ...
            log.debug('Play {}'.format(video))
            if not last_video == video:
                try:
                    player.quit()
                except:
                    killall_omxplayer()
                log.debug('Load new Video: {}'.format(video))
                dbus_name = 'org.mpris.MediaPlayer2.omxplayer{}'.format(player_num)
                player = OMXPlayer(video, args=omxplayer_args, dbus_name=dbus_name, pause=True)
                #log.debug(player.volume())
                player.set_volume(1.5)
                time.sleep(1)

            player.set_alpha(255)
            player.play_sync()
            player.pause()
            player.set_alpha(0)
            player.set_position(0)


            log.debug('Video fertig: {}'.format(video))
            last_video = video

            try:
                # clean queue
                queue.get_nowait()
            except:
                ...
    except KeyboardInterrupt:
        ...
    finally:
        killall_omxplayer()


class VideoPlayer(object):
    def __init__(self, videos):
        self._player_num = 0
        self.player = None
        self.queue = Queue(1)
        self.thread = Process(target=omxplayer_process, args=(self.queue,))

    def play(self, video):
        try:
            self.queue.put(video, block = False)
        except:
            log.debug('Player ist bechäftigt')

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args, **kwargs):
        log.debug('Kill player')
        self.queue.put(False)
        self.thread.join()
        killall_omxplayer()

"""



    def _new_player(self, video, pause=True):
        dbus_name = 'org.mpris.MediaPlayer2.omxplayer{}'.format(self._player_num)
        player = OMXPlayer(video, args=['--no-osd', '-b', '--loop'], dbus_name=dbus_name,
                           pause=pause)
        self._player_num += 1
        return player
        
        
# holds every video in memory, might crash
class VideoPlayer(object):
    def __init__(self, videos):
        self.omxplayers = {}
        for i, video in enumerate(videos):
            dbus_name = 'org.mpris.MediaPlayer2.omxplayer{}'.format(i)
            player = OMXPlayer(video, args=['--no-osd', '-b', '--loop', '--dbus_name', dbus_name], dbus_name=dbus_name, pause=True)
            self.omxplayers[video] = player

    def play(self, video):
        try:
            log.debug('Play {}'.format(video))
            player = self.omxplayers[video]
            player.play_sync()
            player.pause()
        except omxplayer.player.OMXPlayerDeadError:
            raise

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        log.debug('Kill players')
        for k, player in self.omxplayers.items():
            player.quit()
"""



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
            subprocess.call(['sudo', 'rsync', '-av', '--delete', usb_mountpoint, video_path])
            log.info('Dateien wurden kopiert. USB Stick kann jetzt entfernt werden.')

    log.debug("Video Player Dienst wurde gestartet")
    if os.path.isfile(background_image):
        subprocess.call(['sudo', 'fbi', '-T', '1', '-noverbose', '/usr/local/share/rpi-video-player/standbild.jpg'], stdout=subprocess.DEVNULL)
    try:
        videos = find_videos()
        buttons = []
        with VideoPlayer(list(videos.values())) as video_player:
            for pin, video in videos.items():
                button = Button(pin)

                def play(video):
                    def fun():
                        try:
                            video_player.play(video)
                        except BaseException as e:
                            log.critical("{}".format(repr(e)))
                            video_player.__exit__()
                            exit(1)
                    return fun

                button.when_pressed = play(video)
                buttons.append(button)
                log.debug('Video file "{}" on GPIO{}'.format(os.path.basename(video), pin))
            log.debug("Warte auf Signale")
            pause()
    except PinConflict as e:
        log.critical(str(e))
        log.critical("Bitte entfernen Sie alle bis auf ein Video pro Pin und starten Sie den Raspberry pi neu.")
    except KeyboardInterrupt:
        ...
    finally:
        killall_fbi
        killall_omxplayer()


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

