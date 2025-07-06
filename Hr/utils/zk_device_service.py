"""
ZK Device Service for handling fingerprint machine communication
Supports ZK devices via TCP/IP connection
"""

import socket
import struct
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class ZKDeviceService:
    """Service for communicating with ZK fingerprint devices"""
    
    # ZK Protocol Commands
    CMD_CONNECT = 1000
    CMD_EXIT = 1001
    CMD_ENABLEDEVICE = 1002
    CMD_DISABLEDEVICE = 1003
    CMD_ACK_OK = 2000
    CMD_ACK_ERROR = 2001
    CMD_ACK_DATA = 2002
    CMD_PREPARE_DATA = 1500
    CMD_DATA = 1501
    CMD_FREE_DATA = 1502
    CMD_ATTLOG_RRQ = 13
    CMD_CLEAR_DATA = 14
    CMD_CLEAR_ATTLOG = 15
    CMD_DELETE_USER = 18
    CMD_DELETE_USERTEMP = 19
    CMD_CLEAR_ADMIN = 20
    CMD_USERTEMP_RRQ = 9
    CMD_USERTEMP_WRQ = 10
    CMD_OPTIONS_RRQ = 11
    CMD_OPTIONS_WRQ = 12
    CMD_ATTLOG_RRQ = 13
    CMD_CLEAR_DATA = 14
    CMD_CLEAR_ATTLOG = 15
    CMD_DELETE_USER = 18
    CMD_DELETE_USERTEMP = 19
    CMD_CLEAR_ADMIN = 20
    CMD_ENABLE_CLOCK = 57
    CMD_STARTVERIFY = 60
    CMD_STARTENROLL = 61
    CMD_CANCELCAPTURE = 62
    CMD_STATE_RRQ = 64
    CMD_WRITE_LCD = 66
    CMD_CLEAR_LCD = 67
    
    def __init__(self, ip_address: str, port: int = 4370, password: str = ""):
        """
        Initialize ZK device connection
        
        Args:
            ip_address: Device IP address
            port: Device port (default 4370)
            password: Device password if required
        """
        self.ip_address = ip_address
        self.port = port
        self.password = password
        self.socket = None
        self.session_id = 0
        self.reply_id = 0
        self.is_connected = False
        
    def connect(self) -> bool:
        """
        Connect to ZK device
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((self.ip_address, self.port))
            
            # Send connect command
            command = self._create_header(self.CMD_CONNECT, b'')
            self.socket.send(command)
            
            # Receive response
            response = self.socket.recv(1024)
            if len(response) >= 8:
                reply_id, command_id, checksum, session_id = struct.unpack('<HHHH', response[:8])
                if command_id == self.CMD_ACK_OK:
                    self.session_id = session_id
                    self.is_connected = True
                    logger.info(f"Successfully connected to ZK device at {self.ip_address}:{self.port}")
                    return True
                    
            logger.error(f"Failed to connect to ZK device at {self.ip_address}:{self.port}")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to ZK device: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from ZK device
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.socket and self.is_connected:
                # Send exit command
                command = self._create_header(self.CMD_EXIT, b'')
                self.socket.send(command)
                self.socket.close()
                
            self.socket = None
            self.is_connected = False
            self.session_id = 0
            logger.info(f"Disconnected from ZK device at {self.ip_address}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from ZK device: {str(e)}")
            return False
    
    def get_attendance_records(self, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get attendance records from ZK device
        
        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            
        Returns:
            List of attendance records
        """
        if not self.is_connected:
            logger.error("Device not connected")
            return []
            
        try:
            # Disable device to prevent new records during reading
            self._send_command(self.CMD_DISABLEDEVICE)
            
            # Request attendance log data
            self._send_command(self.CMD_ATTLOG_RRQ)
            
            # Receive data
            records = self._receive_attendance_data()
            
            # Enable device again
            self._send_command(self.CMD_ENABLEDEVICE)
            
            # Filter by date if specified
            if start_date or end_date:
                records = self._filter_records_by_date(records, start_date, end_date)
                
            logger.info(f"Retrieved {len(records)} attendance records from ZK device")
            return records
            
        except Exception as e:
            logger.error(f"Error getting attendance records: {str(e)}")
            # Make sure to re-enable device
            try:
                self._send_command(self.CMD_ENABLEDEVICE)
            except:
                pass
            return []
    
    def clear_attendance_records(self) -> bool:
        """
        Clear all attendance records from ZK device
        
        Returns:
            bool: True if successful
        """
        if not self.is_connected:
            logger.error("Device not connected")
            return False
            
        try:
            # Send clear attendance log command
            response = self._send_command(self.CMD_CLEAR_ATTLOG)
            if response:
                logger.info("Successfully cleared attendance records from ZK device")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error clearing attendance records: {str(e)}")
            return False
    
    def get_device_info(self) -> Dict:
        """
        Get device information
        
        Returns:
            Dictionary with device information
        """
        if not self.is_connected:
            return {}
            
        try:
            # This is a simplified version - actual implementation would
            # query specific device parameters
            return {
                'ip_address': self.ip_address,
                'port': self.port,
                'connected': self.is_connected,
                'session_id': self.session_id,
                'device_type': 'ZK Fingerprint Device'
            }
        except Exception as e:
            logger.error(f"Error getting device info: {str(e)}")
            return {}
    
    def _create_header(self, command: int, data: bytes) -> bytes:
        """Create ZK protocol header"""
        checksum = 0
        if data:
            checksum = sum(data) % 65536
            
        header = struct.pack('<HHHH', self.reply_id, command, checksum, self.session_id)
        self.reply_id = (self.reply_id + 1) % 65536
        
        return header + data
    
    def _send_command(self, command: int, data: bytes = b'') -> bool:
        """Send command to ZK device"""
        try:
            packet = self._create_header(command, data)
            self.socket.send(packet)
            
            # Receive response
            response = self.socket.recv(1024)
            if len(response) >= 8:
                reply_id, command_id, checksum, session_id = struct.unpack('<HHHH', response[:8])
                return command_id == self.CMD_ACK_OK
            return False
            
        except Exception as e:
            logger.error(f"Error sending command {command}: {str(e)}")
            return False
    
    def _receive_attendance_data(self) -> List[Dict]:
        """Receive and parse attendance data from device"""
        records = []
        
        try:
            # This is a simplified implementation
            # Actual ZK protocol parsing would be more complex
            
            # Receive data size first
            response = self.socket.recv(1024)
            if len(response) < 8:
                return records
                
            # Parse response header
            reply_id, command_id, checksum, session_id = struct.unpack('<HHHH', response[:8])
            
            if command_id == self.CMD_ACK_DATA:
                # Get data size from response
                data_size = len(response) - 8
                data = response[8:]
                
                # Parse attendance records (simplified)
                # Each record is typically 16 bytes in ZK format
                record_size = 16
                num_records = data_size // record_size
                
                for i in range(num_records):
                    record_data = data[i * record_size:(i + 1) * record_size]
                    if len(record_data) >= record_size:
                        record = self._parse_attendance_record(record_data)
                        if record:
                            records.append(record)
                            
        except Exception as e:
            logger.error(f"Error receiving attendance data: {str(e)}")
            
        return records
    
    def _parse_attendance_record(self, data: bytes) -> Optional[Dict]:
        """Parse individual attendance record from binary data"""
        try:
            # Simplified parsing - actual ZK format may vary
            if len(data) < 16:
                return None
                
            # Extract fields (this is a simplified example)
            user_id = struct.unpack('<H', data[0:2])[0]
            timestamp = struct.unpack('<I', data[4:8])[0]
            verify_type = data[8]
            in_out_mode = data[9]
            
            # Convert timestamp to datetime
            dt = datetime.fromtimestamp(timestamp, tz=timezone.get_current_timezone())
            
            return {
                'user_id': str(user_id),
                'timestamp': dt,
                'verify_type': verify_type,
                'in_out_mode': in_out_mode,
                'raw_data': data.hex()
            }
            
        except Exception as e:
            logger.error(f"Error parsing attendance record: {str(e)}")
            return None
    
    def _filter_records_by_date(self, records: List[Dict], 
                               start_date: Optional[datetime], 
                               end_date: Optional[datetime]) -> List[Dict]:
        """Filter records by date range"""
        filtered_records = []
        
        for record in records:
            record_date = record.get('timestamp')
            if not record_date:
                continue
                
            if start_date and record_date < start_date:
                continue
                
            if end_date and record_date > end_date:
                continue
                
            filtered_records.append(record)
            
        return filtered_records
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
