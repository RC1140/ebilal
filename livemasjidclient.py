# -*- coding: utf-8 -*-
#from gluon import *
import paho.mqtt.client as mqtt
import sys
import time
import argparse
import json
import logging
import logging.config
import imp
import os
import subprocess
import alsaaudio

logger = logging.getLogger()

def load_config():
    global server_url, mounts
    with open('/opt/ebilal/config.json', 'r') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
            server_url = config['DEFAULT']['SERVER_URL'] 
            mounts = config['DEFAULT']['MOUNTS']

class LivemasjidClient:
    """User Object"""
    def __init__(self, mountToPlay, config_url):
        self.mountToPlay = mountToPlay
        #self.Instance = vlc.Instance()
        #self.player = self.Instance.media_player_new()
        self.client = mqtt.Client()
        self.baseURL = config_url
        self.current_vol = 50
        self.livestreams = []
        self.playing = None
        self.mixer = alsaaudio.Mixer()
    
    def set_mounts(self,mounts):
        self.mountToPlay = mounts

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self,client, userdata, flags, rc):
        logger.info("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("mounts/#")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self,client, userdata, msg):
        logger.debug(msg.topic+" "+str(msg.payload))
        message = msg.topic.split('/')
        if (message[1] in self.mountToPlay):
            if ("started" in msg.payload):
                self.playmount(message[1])
                self.livestreams.append(message[1])
            elif "stopped" in msg.payload:
                self.stop()
                self.livestreams.remove(message[1])

    def playmount(self,mount):
        logger.debug("Playing mount "+mount)
        self.playurl(self.baseURL+mount)
        self.playing = mount

    def playurl(self,url):
        logger.debug("Starting media player")
        self.process = subprocess.call(["ffplay","-autoexit" ,url])
        #Media = self.Instance.media_new(url)
        #Media.get_mrl()
        #self.player.set_media(Media)
        #self.player.audio_set_volume(self.current_vol)
        #self.player.play()

    def stop(self):
        logger.debug("stopping media player")
        self.process.kill()
        #self.player.stop()

    def tunein(self,mount,start=False):
        self.mountToPlay=mount
        if start:
            self.playmount(mount)

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect("livemasjid.com", 1883, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.client.loop_start()
        #client.loop_forever()

    def disconnect(self):
        self.client.loop_stop()
    
    def volup(self):
        self.current_vol = self.mixer.getvolume() + 10
        self.mixer.setvolume((self.current_vol))
    
    def voldown(self):
        self.current_vol =  self.mixer.getvolume() - 10
        self.mixer.setvolume(self.current_vol)

    def getlivestreams(self):
        return self.livestreams

def main():
    mounts = ["activestream"]
    load_config()
    if len(sys.argv) > 1:
        mounts = sys.argv[1].split(',')
    logger.info("Starting..")
    parser = argparse.ArgumentParser(description='Linux client for Livemasjid.com streams.')
    livemasjid = LivemasjidClient(mounts,server_url)
    livemasjid.connect()
    try:
        imp.find_module('phatbeat')
        found = True
    except ImportError:
        found = False
    if found:
        import phatbeat
        phatbeat.set_all(0,128,0,0.1)
        phatbeat.show()
        time.sleep(1)
        phatbeat.clear()
        phatbeat.show()

        @phatbeat.on(phatbeat.BTN_VOLDN)
        def pb_volume_down(pin):
            livemasjid.voldown()

        @phatbeat.on(phatbeat.BTN_VOLUP)
        def pb_volume_up(pin):
            livemasjid.volup()

        @phatbeat.on(phatbeat.BTN_PLAYPAUSE)
        def pb_play_pause(pin):
            time.sleep(0.1)
            phatbeat.clear()
            phatbeat.show()
            if livemasjid.player.is_playing:
                livemasjid.player.pause
            else: livemasjid.player.play

        @phatbeat.on(phatbeat.BTN_FASTFWD)
        def pb_fast_forward(pin):
            try:
                index = livemasjid.livestreams.index(livemasjid.playing)
                livemasjid.playmount(livemasjid.getlivestreams()[index+1])
            except Exception as e:
                livemasjid.playmount(livemasjid.getlivestreams()[0])
                logger.error(e.message, e.args)

        @phatbeat.on(phatbeat.BTN_REWIND)
        def pb_rewind(pin):
            try:
                index = livemasjid.livestreams.index(livemasjid.playing)
                livemasjid.playmount(livemasjid.getlivestreams()[index-1])
            except Exception as e:
                livemasjid.playmount(livemasjid.getlivestreams()[0])
                logger.error(e.message, e.args)

        @phatbeat.on(phatbeat.BTN_ONOFF)
        def perform_shutdown(pin):
            os.system("sudo shutdown -h now")

    while True:
        time.sleep(60)
        logger.debug("reloading config file")
        #load_config()
        #livemasjid.set_mounts(mounts)

if __name__ == "__main__":
    main()
