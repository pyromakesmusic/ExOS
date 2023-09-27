"""
This should build up the OSC networking capability to start implementing physics control.
"""

from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from pythonosc import osc_server
import asyncio
import argparse
import time
import math

"""
GLOBAL CONFIGURATION
"""
ip = "127.0.0.1"
port = 5005

client = SimpleUDPClient(ip, port)  # Create client
"""
FUNCTION DEFINITIONS
"""


async def async_sender_loop():
    """Example main loop that only runs for 10 iterations before finishing"""
    for i in range(100):
        client.send_message("/some/address", 123)  # Send float message
        client.send_message("/some/address", [1, 2., "hello"])  # Send message with int, float and string
        await asyncio.sleep(1)


async def init_main(dispatcher):
    """
    Multithreading receiver loop.
    """
    server = osc_server.AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()
    await async_sender_loop()
    transport.close()


class BlockingServer:

    def __init__(self):
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/filter", print)

        self.dispatcher.map("/volume", self.print_volume_handler, "Volume")
        self.dispatcher.map("/logvolume", self.print_compute_handler, "Log volume", math.log)

        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1", help="The IP address to listen on")
        parser.add_argument("--port", type=int, default=5005, help="The port to listen on")
        args = parser.parse_args()

        server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), self.dispatcher)

        print("Serving on {}".format(server.server_address))
        server.serve_forever()

    def print_volume_handler(self, args, volume):
        print("[{0}] ~ {1}".format(args[0], volume))

    def print_compute_handler(self, args, volume):
        try:
            print("[{0}] ~ {1}".format(args[0], args[1](volume)))
        except ValueError:
            pass


if __name__ == "__main__":
    """
    Starting with a blocking threaded server then trying to convert to multithreaded.
    """




