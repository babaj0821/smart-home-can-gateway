import socket
import struct


class CANInterface:

    CAN_FRAME_FORMAT = "=IB3x8s"  # Linux classic struct can_frame (16 bytes)
    CAN_FRAME_SIZE = struct.calcsize(CAN_FRAME_FORMAT)

    def __init__(self, interface="can0"):
        self.interface = interface
        self.sock = None

    def connect(self):
        """
        Create the SocketCAN socket and bind it to can0.
        """

        self.sock = socket.socket(
            socket.PF_CAN,
            socket.SOCK_RAW,
            socket.CAN_RAW
        )

        self.sock.bind((self.interface,))
        # TODO: Decide whether receive should be blocking or non-blocking.
        # TODO:
        # Later decide whether we want blocking,
        # timeout, or non-blocking receiving.

    def send(self, can_id, data):
        """
        Send one classic CAN frame.
        """

        if self.sock is None:
            raise RuntimeError("CAN interface is not connected")

        if not isinstance(data, bytes):
            raise TypeError("CAN data must be bytes")

        if len(data) > 8:
            raise ValueError("Classic CAN payload cannot exceed 8 bytes")

        frame = struct.pack(
            self.CAN_FRAME_FORMAT,
            can_id,
            len(data),
            data.ljust(8, b"\x00")
        )

        self.sock.send(frame)

    def receive(self):
        """
        Receive one CAN frame.

        TODO:
        Complete/modify this function yourself.
        """

        frame = self.sock.recv(self.CAN_FRAME_SIZE)

        can_id, data_length, data = struct.unpack(
            self.CAN_FRAME_FORMAT,
            frame
        )

        data = data[:data_length]

        return can_id, data

    def close(self):

        if self.sock is not None:
            self.sock.close()
            self.sock = None
