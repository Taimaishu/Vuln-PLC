#!/usr/bin/env python3
"""
Basic Siemens S7 Protocol Server
Simplified implementation for educational purposes

S7comm protocol basics:
- Runs over ISO-on-TCP (port 102)
- Connection-oriented
- PDU-based communication
- Supports reading/writing data blocks, memory areas
"""

import socket
import threading
import struct
import logging
from enum import Enum
from typing import Dict, List, Tuple
import shared_state

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class S7AreaCode(Enum):
    """S7 memory area codes"""
    SYSINFO = 0x03
    SYSFLAGS = 0x05
    ANAIN = 0x06
    ANAOUT = 0x07
    COUNTER = 0x1C
    TIMER = 0x1D
    IPI = 0x80
    IPQ = 0x81
    IPM = 0x82
    DB = 0x84  # Data Block

class S7Function(Enum):
    """S7 function codes"""
    READ_VAR = 0x04
    WRITE_VAR = 0x05
    DOWNLOAD = 0x1A
    UPLOAD = 0x1B
    PLC_CONTROL = 0x28
    PLC_STOP = 0x29

class S7Server:
    """
    Basic S7comm protocol server

    Implements simplified S7 protocol for:
    - Reading data blocks
    - Writing data blocks
    - PLC status queries
    - Basic PLC control

    INTENTIONALLY VULNERABLE for training:
    - No authentication
    - No encryption
    - Accepts all commands
    """

    def __init__(self, host='0.0.0.0', port=102, plc_id='plc1'):
        self.host = host
        self.port = port
        self.plc_id = plc_id
        self.running = False
        self.server_socket = None

        # S7 memory areas
        self.data_blocks: Dict[int, bytearray] = {}
        self.inputs = bytearray(1024)   # Input area (I)
        self.outputs = bytearray(1024)  # Output area (Q)
        self.markers = bytearray(1024)  # Memory area (M)

        # PLC state
        self.plc_mode = 'RUN'  # RUN, STOP, PROGRAM

        # Initialize data blocks
        for db_num in range(1, 11):
            self.data_blocks[db_num] = bytearray(1024)

        shared_state.init_state()

    def start(self):
        """Start S7 server"""
        if self.running:
            return

        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)

            log.info(f"""
╔═══════════════════════════════════════════════════════════╗
║  Siemens S7 Protocol Server (Educational/Vulnerable)      ║
╚═══════════════════════════════════════════════════════════╝

S7 Server: {self.host}:{self.port}
PLC ID: {self.plc_id}
Mode: {self.plc_mode}

VULNERABILITIES (Intentional):
  • No authentication required
  • No encryption
  • Accepts PLC STOP commands
  • No input validation
  • No access control

MEMORY AREAS:
  • Data Blocks: DB1-DB10 (1KB each)
  • Inputs (I): 1KB
  • Outputs (Q): 1KB
  • Markers (M): 1KB

TEST COMMANDS (using python snap7 library):
  import snap7
  plc = snap7.client.Client()
  plc.connect('{self.host}', 0, 1, {self.port})

  # Read DB1, starting at byte 0, 10 bytes
  data = plc.db_read(1, 0, 10)

  # Write to DB1
  plc.db_write(1, 0, bytearray([0x01, 0x02, 0x03]))

  # Get PLC status
  status = plc.get_cpu_state()

⚠️  WARNING: This is an INTENTIONALLY VULNERABLE implementation
    for security training purposes only!
            """)

            # Accept connections
            threading.Thread(target=self._accept_loop, daemon=True).start()

        except Exception as e:
            log.error(f"Failed to start S7 server: {e}")
            self.running = False

    def stop(self):
        """Stop S7 server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        log.info("[S7 Server] Stopped")

    def _accept_loop(self):
        """Accept client connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                log.info(f"[S7 Server] Client connected: {addr}")

                # Handle client in separate thread
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True
                ).start()

            except Exception as e:
                if self.running:
                    log.error(f"[S7 Server] Accept error: {e}")

    def _handle_client(self, client_socket: socket.socket, addr: Tuple):
        """Handle client connection"""
        try:
            while self.running:
                # Receive TPKT header (4 bytes)
                tpkt_header = client_socket.recv(4)
                if not tpkt_header or len(tpkt_header) < 4:
                    break

                # Parse TPKT
                version = tpkt_header[0]
                reserved = tpkt_header[1]
                length = struct.unpack('>H', tpkt_header[2:4])[0]

                # Receive remaining data
                data = client_socket.recv(length - 4)

                # Parse and handle S7 request
                response = self._handle_s7_request(data, addr)

                if response:
                    client_socket.send(response)

        except Exception as e:
            log.error(f"[S7 Server] Client error: {e}")
        finally:
            client_socket.close()
            log.info(f"[S7 Server] Client disconnected: {addr}")

    def _handle_s7_request(self, data: bytes, addr: Tuple) -> bytes:
        """
        Parse and handle S7 request

        Simplified S7 protocol handling:
        - Just enough to demonstrate concept
        - Real S7 protocol is much more complex
        """
        if len(data) < 10:
            return None

        try:
            # Parse COTP header (3 bytes minimum)
            cotp_length = data[0]
            cotp_pdu_type = data[1]

            # Check if connection request
            if cotp_pdu_type == 0xE0:
                # Connection Request - send Connection Confirm
                return self._build_connection_confirm()

            # Parse S7 header (starts after COTP)
            s7_start = cotp_length + 1
            if len(data) < s7_start + 10:
                return None

            s7_header = data[s7_start:]
            protocol_id = s7_header[0]
            msg_type = s7_header[1]
            reserved = struct.unpack('>H', s7_header[2:4])[0]
            pdu_ref = struct.unpack('>H', s7_header[4:6])[0]
            param_length = struct.unpack('>H', s7_header[6:8])[0]
            data_length = struct.unpack('>H', s7_header[8:10])[0]

            # Parse parameters
            if param_length > 0:
                params = s7_header[10:10+param_length]
                function = params[0]

                log.info(f"[S7 Server] Request from {addr}: function=0x{function:02X}")

                # Handle different functions
                if function == S7Function.READ_VAR.value:
                    return self._handle_read_var(pdu_ref, params, data)
                elif function == S7Function.WRITE_VAR.value:
                    return self._handle_write_var(pdu_ref, params, data)
                elif function == S7Function.PLC_CONTROL.value:
                    return self._handle_plc_control(pdu_ref, params)
                else:
                    log.warning(f"[S7 Server] Unsupported function: 0x{function:02X}")

        except Exception as e:
            log.error(f"[S7 Server] Request handling error: {e}")

        return None

    def _build_connection_confirm(self) -> bytes:
        """Build COTP Connection Confirm"""
        # TPKT Header
        tpkt = bytearray([
            0x03,  # Version
            0x00,  # Reserved
            0x00, 0x16  # Length (22 bytes)
        ])

        # COTP Connection Confirm
        cotp = bytearray([
            0x11,  # Length
            0xD0,  # PDU type (Connection Confirm)
            0x00, 0x01,  # Destination reference
            0x00, 0x00,  # Source reference
            0x00,  # Class/Option
        ])

        # S7 Communication Setup
        s7_setup = bytearray([
            0xC0, 0x01,  # Parameter code
            0x0A,  # Parameter length
            0xC1, 0x02, 0x01, 0x00,  # PDU size (256 bytes)
            0xC2, 0x02, 0x01, 0x00,  # PDU size
        ])

        return bytes(tpkt + cotp + s7_setup)

    def _handle_read_var(self, pdu_ref: int, params: bytes, data: bytes) -> bytes:
        """Handle read variable request"""
        # Simplified - return dummy data
        # Real implementation would parse area, DB number, offset, length

        # Build response
        response = bytearray()

        # TPKT Header
        response += bytearray([0x03, 0x00, 0x00, 0x1F])  # Length will be updated

        # COTP
        response += bytearray([0x02, 0xF0, 0x80])

        # S7 Header
        response += bytearray([
            0x32,  # Protocol ID
            0x03,  # Message type (Ack_Data)
            0x00, 0x00,  # Reserved
        ])
        response += struct.pack('>H', pdu_ref)  # PDU reference
        response += bytearray([0x00, 0x02])  # Param length
        response += bytearray([0x00, 0x08])  # Data length

        # Parameters
        response += bytearray([0x00, 0x00])  # Error class/code

        # Data
        response += bytearray([0xFF, 0x04, 0x00, 0x08])  # Return code, transport size, length
        response += bytearray([0x00, 0x01, 0x02, 0x03])  # Dummy data

        # Update length
        total_length = len(response)
        response[2:4] = struct.pack('>H', total_length)

        log.info(f"[S7 Server] Read variable response sent")
        return bytes(response)

    def _handle_write_var(self, pdu_ref: int, params: bytes, data: bytes) -> bytes:
        """Handle write variable request"""
        log.warning(f"[S7 Server] 🚨 WRITE operation detected (no auth check!)")

        # Build success response
        response = bytearray()

        # TPKT Header
        response += bytearray([0x03, 0x00, 0x00, 0x16])

        # COTP
        response += bytearray([0x02, 0xF0, 0x80])

        # S7 Header
        response += bytearray([
            0x32,  # Protocol ID
            0x03,  # Message type (Ack_Data)
            0x00, 0x00,  # Reserved
        ])
        response += struct.pack('>H', pdu_ref)
        response += bytearray([0x00, 0x02])  # Param length
        response += bytearray([0x00, 0x01])  # Data length

        # Parameters (success)
        response += bytearray([0x00, 0x00])

        # Data (write result)
        response += bytearray([0xFF])  # Success

        return bytes(response)

    def _handle_plc_control(self, pdu_ref: int, params: bytes) -> bytes:
        """Handle PLC control command (START/STOP)"""
        # VULNERABILITY: No authentication for PLC control!
        if len(params) > 7:
            service = params[7]

            if service == 0x00:  # PLC STOP
                self.plc_mode = 'STOP'
                log.error("[S7 Server] 🚨🚨🚨 PLC STOP command received (no auth!)")
                shared_state.update_state(f'{self.plc_id}_mode', 'STOP')
                shared_state.update_state(f'{self.plc_id}_emergency_stop', True)

            elif service == 0x01:  # PLC START
                self.plc_mode = 'RUN'
                log.info("[S7 Server] PLC START command received")
                shared_state.update_state(f'{self.plc_id}_mode', 'RUN')

        # Build response
        response = bytearray([0x03, 0x00, 0x00, 0x13])  # TPKT
        response += bytearray([0x02, 0xF0, 0x80])  # COTP
        response += bytearray([0x32, 0x03, 0x00, 0x00])  # S7 header
        response += struct.pack('>H', pdu_ref)
        response += bytearray([0x00, 0x00, 0x00, 0x00])  # No params/data

        return bytes(response)

    def read_db(self, db_num: int, offset: int, length: int) -> bytes:
        """Read from data block"""
        if db_num in self.data_blocks:
            return bytes(self.data_blocks[db_num][offset:offset+length])
        return bytes(length)

    def write_db(self, db_num: int, offset: int, data: bytes):
        """Write to data block"""
        if db_num not in self.data_blocks:
            self.data_blocks[db_num] = bytearray(1024)

        end = offset + len(data)
        if end <= len(self.data_blocks[db_num]):
            self.data_blocks[db_num][offset:end] = data
            log.info(f"[S7 Server] Wrote {len(data)} bytes to DB{db_num} @ offset {offset}")


if __name__ == '__main__':
    # Start S7 server
    server = S7Server(host='0.0.0.0', port=102, plc_id='plc1_s7')

    try:
        server.start()

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping S7 server...")
        server.stop()
