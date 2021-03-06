from panda import Panda
from nose.tools import timed, assert_equal, assert_less, assert_greater
import time
import os
import random

def connect_wo_esp():
  # connect to the panda
  p = Panda()

  # power down the ESP
  p.set_esp_power(False)
  return p

  # clear old junk
  while len(p.can_recv()) > 0:
    pass

def connect_wifi():
  p = Panda()
  ssid, pw = p.get_serial()
  ssid = ssid.strip("\x00")
  assert(ssid.isalnum())
  assert(pw.isalnum())
  ssid = "panda-" + ssid

  # Mac OS X only
  # TODO: Ubuntu
  os.system("networksetup -setairportnetwork en0 %s %s" % (ssid, pw))

def time_many_sends(p, bus, precv=None, msg_count=100, msg_id=None):
  if precv == None:
    precv = p
  if msg_id == None:
    msg_id = random.randint(0x100, 0x200)

  st = time.time()
  p.can_send_many([(msg_id, 0, "\xaa"*8, bus)]*msg_count)
  r = []

  while len(r) < (msg_count*2) and (time.time() - st) < 3:
    r.extend(precv.can_recv())

  sent_echo = filter(lambda x: x[3] == 0x80 | bus and x[0] == msg_id, r)
  loopback_resp = filter(lambda x: x[3] == bus and x[0] == msg_id, r)

  assert_equal(len(sent_echo), msg_count)
  assert_equal(len(loopback_resp), msg_count)

  et = (time.time()-st)*1000.0
  comp_kbps = (1+11+1+1+1+4+8*8+15+1+1+1+7)*msg_count / et

  return comp_kbps

