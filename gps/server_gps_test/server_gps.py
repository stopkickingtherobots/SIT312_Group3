import pubnub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNOperationType, PNStatusCategory   

from dataclasses import dataclass

@dataclass
class Data_Segment:
    data_type: str
    sequence: int
    total_sequence: int
    data: list

def publish_callback(result, status):
    pass
    # Handle PNPublishResult and PNStatus

def main(gps_queue):

    # PunNub Instance

    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = "sub-c-5f7c7648-c99c-11e9-ac59-7e2323a85324"
    pnconfig.publish_key = "pub-c-af13eaae-73e7-4c64-a7e8-4ec6c0dc13d1"
    pnconfig.ssl = False
    pubnub = PubNub(pnconfig)

    while(True):
        msg = gps_queue.get() # Will block until message is recieved

        latitude = msg.data[0] # data is an array
        longitude = msg.data[1]
        timestamp = msg.data[2]

        if latitude and longitude is not None:
            dictionary = {"latitude": latitude, "longitude": longitude}
            pubnub.publish().channel('blue').message(dictionary).pn_async(publish_callback)
            print('eol')  # End of Line