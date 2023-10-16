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
FUNCTION DEFINITIONS
"""


async def async_sender_loop(client):
    """Example main loop that only runs for 10 iterations before finishing"""
    for i in range(100):
        client.send_message("/some/address", 123)  # Send float message
        client.send_message("/some/address", [1, 2., "hello"])  # Send message with int, float and string
        await asyncio.sleep(1)


async def init_main(dispatcher, ip, port):
    """
    Multithreading receiver loop.
    """
    server = osc_server.AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()
    await async_sender_loop()
    transport.close()


class SimpleSender:
  def __init__(self, ip, port):
    SimpleUDPClient.__init__(ip, port)

class ThreadedServer:
    """
    Multithreading now.
    """
    def __init__(self, ip, port):
        self.dispatcher = Dispatcher()
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--ip", default=ip, help="The IP address to listen on")
        self.parser.add_argument("--port", type=int, default=port, help="The port to listen on")
        self.args = self.parser.parse_args()
        self.ip = ip
        self.port = port
        self.server = osc_server.AsyncIOOSCUDPServer((self.ip, self.port), self.dispatcher, asyncio.get_event_loop())
        self.transport = None
        self.protocol = None

    async def make_endpoint(self):

        self.transport, self.protocol = self.server.create_serve_endpoint()
        print("Serving on {}".format(self.ip))

    async def launch(self, main_loop):
        await main_loop()
        self.transport.close()

    def map(self, pattern, func, *args, **kwargs):
        """
        pattern: string var defining the OSC pattern to be recognized
        func: the function to map to
        args: any args for the function, this may need to be *args and **kwargs - needs more research
        """
        self.dispatcher.map(pattern, func, args)

class BlockingServer:
    """
    Initializes with an IP formatted as string and port formatted as integer.
    """

    def __init__(self, ip, port):
        self.dispatcher = Dispatcher()

        # self.dispatcher.map("/filter", print)
        # self.dispatcher.map("/volume", self.print_volume_handler, "Volume")
        # self.dispatcher.map("/logvolume", self.print_compute_handler, "Log volume", math.log)

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--ip", default=ip, help="The IP address to listen on")
        self.parser.add_argument("--port", type=int, default=port, help="The port to listen on")
        self.args = self.parser.parse_args()

        self.server = None

    # def print_volume_handler(self, args, volume):
    #     print("[{0}] ~ {1}".format(args[0], volume))
    #
    # def print_compute_handler(self, args, volume):
    #     try:
    #         print("[{0}] ~ {1}".format(args[0], args[1](volume)))
    #     except ValueError:
    #         pass

    def map(self, pattern, func, *args, **kwargs):
        """
        pattern: string var defining the OSC pattern to be recognized
        func: the function to map to
        args: any args for the function, this may need to be *args and **kwargs - needs more research
        """
        self.dispatcher.map(pattern, func, args)

    def serve_forever(self):
        self.server = osc_server.ThreadingOSCUDPServer((self.args.ip, self.args.port), self.dispatcher)
        print("Serving on {}".format(self.server.server_address))
        self.server.serve_forever()

if __name__ == "__main__":
    """
    Starting with a blocking threaded server then trying to convert to multithreaded.
    UPDATE 10.16.2023
    
    Looks like multithreading is the only way this is getting done :))))
    """




