#!/usr/bin/env python3
"""
Standalone Modbus TCP Server - No Flask dependencies
Just tests that our Modbus implementation works
"""

import socket
import threading
import struct
import sys
import os

# Add core directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
import shared_state

class ModbusTCPServer:
    """Minimal Modbus TCP Server - Improved Stability"""

    def __init__(self, host='0.0.0.0', port=5555, max_connections=50):  # Use different port
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.connection_semaphore = threading.Semaphore(max_connections)

    def start(self):
        """Start the Modbus TCP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)  # Allow graceful shutdown
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"[MODBUS] Server started on {self.host}:{self.port}")
            print(f"[MODBUS] Test with: python3 quick_test.py")

            while self.running:
                try:
                    # Accept client connections
                    client_socket, address = self.server_socket.accept()
                    print(f"[MODBUS] Client connected from {address}")

                    # Handle client with semaphore
                    client_thread = threading.Thread(
                        target=self._handle_client_with_semaphore,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()

                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    print("\n[MODBUS] Shutting down...")
                    break
                except Exception as e:
                    if self.running:
                        print(f"[MODBUS] Error accepting connection: {e}")

        except Exception as e:
            print(f"[MODBUS] Failed to start server: {e}")

    def stop(self):
        """Stop the Modbus TCP server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def recv_exact(self, sock, size):
        """Receive exactly 'size' bytes from socket"""
        data = b''
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Socket closed before receiving all data")
            data += chunk
        return data

    def _handle_client_with_semaphore(self, client_socket, address):
        """Wrapper to handle client with connection semaphore"""
        with self.connection_semaphore:
            self.handle_client(client_socket, address)

    def handle_client(self, client_socket, address):
        """Handle a client connection"""
        try:
            while True:
                # Read MBAP header (7 bytes) - use recv_exact for message safety
                header = self.recv_exact(client_socket, 7)

                # Parse MBAP header
                transaction_id, protocol_id, length, unit_id = struct.unpack('>HHHB', header)

                # Log invalid protocol IDs (educational - helps students learn)
                if protocol_id != 0:
                    print(f"[MODBUS] WARNING: Non-standard protocol ID {protocol_id} from {address} (expected 0)")

                # Read PDU (Protocol Data Unit) - use recv_exact for message safety
                pdu = self.recv_exact(client_socket, length - 1)  # -1 because unit_id already read

                print(f"[MODBUS] Request from {address}: Trans={transaction_id}, Unit={unit_id}, PDU={pdu.hex()}")

                # Parse function code
                function_code = pdu[0]

                # Process request and generate response
                response_pdu = self.process_request(function_code, pdu[1:])

                # Build MBAP response header
                response_length = len(response_pdu) + 1  # +1 for unit_id
                response_header = struct.pack('>HHHB', transaction_id, protocol_id, response_length, unit_id)

                # Send response
                response = response_header + response_pdu
                client_socket.send(response)
                print(f"[MODBUS] Response: {response.hex()}")

        except Exception as e:
            print(f"[MODBUS] Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"[MODBUS] Client {address} disconnected")

    def process_request(self, function_code, data):
        """Process Modbus request and return response PDU"""
        try:
            if function_code == 0x03:
                # Read Holding Registers
                return self.read_holding_registers(data)
            elif function_code == 0x06:
                # Write Single Register
                return self.write_single_register(data)
            elif function_code == 0x10:
                # Write Multiple Registers
                return self.write_multiple_registers(data)
            else:
                # Unsupported function code
                return struct.pack('B', function_code | 0x80) + struct.pack('B', 0x01)

        except Exception as e:
            print(f"[MODBUS] Error processing request: {e}")
            # Return exception response
            return struct.pack('B', function_code | 0x80) + struct.pack('B', 0x04)

    def read_holding_registers(self, data):
        """Function Code 0x03: Read Holding Registers"""
        start_addr, count = struct.unpack('>HH', data[:4])

        print(f"[MODBUS] Read Holding Registers: addr={start_addr}, count={count}")

        # Read values from shared state
        values = []
        for i in range(count):
            register = start_addr + i
            value = shared_state.state_to_register(register)
            values.append(value)

        # Build response
        byte_count = count * 2
        response = struct.pack('BB', 0x03, byte_count)
        for value in values:
            response += struct.pack('>H', value)

        return response

    def write_single_register(self, data):
        """Function Code 0x06: Write Single Register"""
        addr, value = struct.unpack('>HH', data[:4])

        print(f"[MODBUS] Write Single Register: addr={addr}, value={value}")

        # Convert register to state and update
        key, converted_value = shared_state.register_to_state(addr, value)
        if key:
            shared_state.update_state(key, converted_value)
            print(f"[MODBUS] Updated {key} = {converted_value}")

        # Echo request as response
        return struct.pack('B', 0x06) + data[:4]

    def write_multiple_registers(self, data):
        """Function Code 0x10: Write Multiple Registers"""
        start_addr, count, byte_count = struct.unpack('>HHB', data[:5])

        print(f"[MODBUS] Write Multiple Registers: addr={start_addr}, count={count}")

        # Parse values
        values_data = data[5:5+byte_count]
        values = []
        for i in range(count):
            value = struct.unpack('>H', values_data[i*2:(i+1)*2])[0]
            values.append(value)

        # Write to state
        for i, value in enumerate(values):
            register = start_addr + i
            key, converted_value = shared_state.register_to_state(register, value)
            if key:
                shared_state.update_state(key, converted_value)
                print(f"[MODBUS] Updated {key} = {converted_value}")

        # Build response
        return struct.pack('>BHH', 0x10, start_addr, count)


if __name__ == '__main__':
    print("=" * 70)
    print("  STANDALONE MODBUS TCP SERVER")
    print("  Testing our Modbus implementation without Flask")
    print("=" * 70)
    print()

    # Initialize shared state
    shared_state.init_state()
    print("[INIT] Shared state initialized")

    # Start server on port 5555 (avoid conflict with port 5502)
    server = ModbusTCPServer(host='0.0.0.0', port=5555)

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server stopped")
        server.stop()
