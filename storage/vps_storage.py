"""
VPS Storage Backend for GoDaddy VPS
Uploads files to VPS via SFTP and serves them via HTTP
"""
import os
import paramiko
import logging
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class VPSStorage(Storage):
    """
    Custom storage backend that uploads files to GoDaddy VPS via SFTP
    and serves them via HTTP
    """
    
    def __init__(self):
        self.vps_host = getattr(settings, 'VPS_HOST', None)
        self.vps_port = getattr(settings, 'VPS_PORT', 22)
        self.vps_username = getattr(settings, 'VPS_USERNAME', None)
        self.vps_password = getattr(settings, 'VPS_PASSWORD', None)
        self.vps_key_path = getattr(settings, 'VPS_KEY_PATH', None)
        self.vps_base_path = getattr(settings, 'VPS_BASE_PATH', '/var/www/media')
        self.vps_base_url = getattr(settings, 'VPS_BASE_URL', None)
        
        if not self.vps_host:
            raise ValueError("VPS_HOST must be set in settings")
        if not self.vps_username:
            raise ValueError("VPS_USERNAME must be set in settings")
        if not self.vps_base_url:
            raise ValueError("VPS_BASE_URL must be set in settings")
    
    def _get_ssh_client(self):
        """Create and return SSH client connection"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if self.vps_key_path and os.path.exists(self.vps_key_path):
                # Use SSH key authentication
                ssh.connect(
                    self.vps_host,
                    port=self.vps_port,
                    username=self.vps_username,
                    key_filename=self.vps_key_path,
                    timeout=10
                )
            elif self.vps_password:
                # Use password authentication
                ssh.connect(
                    self.vps_host,
                    port=self.vps_port,
                    username=self.vps_username,
                    password=self.vps_password,
                    timeout=10
                )
            else:
                raise ValueError("Either VPS_PASSWORD or VPS_KEY_PATH must be set")
            
            return ssh
        except Exception as e:
            logger.error(f"Failed to connect to VPS: {str(e)}")
            raise
    
    def _get_sftp_client(self, ssh_client):
        """Get SFTP client from SSH client"""
        return ssh_client.open_sftp()
    
    def _ensure_directory_exists(self, sftp, remote_path):
        """Ensure remote directory exists"""
        dir_path = os.path.dirname(remote_path)
        if dir_path == '' or dir_path == '/':
            return
        
        # Create directory structure
        parts = dir_path.strip('/').split('/')
        current_path = ''
        
        for part in parts:
            if current_path:
                current_path = f"{current_path}/{part}"
            else:
                current_path = f"/{part}"
            
            try:
                sftp.stat(current_path)
            except IOError:
                # Directory doesn't exist, create it
                sftp.mkdir(current_path)
                logger.info(f"Created directory: {current_path}")
    
    def _save(self, name, content):
        """Save file to VPS"""
        ssh = None
        sftp = None
        
        try:
            # Read file content
            if hasattr(content, 'read'):
                file_content = content.read()
            else:
                file_content = content
            
            # Build remote path
            remote_path = os.path.join(self.vps_base_path, name).replace('\\', '/')
            
            # Connect to VPS
            ssh = self._get_ssh_client()
            sftp = self._get_sftp_client(ssh)
            
            # Ensure directory exists
            self._ensure_directory_exists(sftp, remote_path)
            
            # Write file to VPS
            with sftp.open(remote_path, 'wb') as remote_file:
                remote_file.write(file_content)
            
            logger.info(f"File saved to VPS: {remote_path}")
            
            # Return URL
            return self.url(name)
            
        except Exception as e:
            logger.error(f"Failed to save file to VPS: {str(e)}")
            raise
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
    
    def _open(self, name, mode='rb'):
        """Open file from VPS (not typically used, but required by Storage interface)"""
        raise NotImplementedError("Reading files from VPS is not implemented. Use HTTP URL instead.")
    
    def _path(self, name):
        """Return local path (not applicable for VPS storage)"""
        return None
    
    def exists(self, name):
        """Check if file exists on VPS"""
        ssh = None
        sftp = None
        
        try:
            remote_path = os.path.join(self.vps_base_path, name).replace('\\', '/')
            ssh = self._get_ssh_client()
            sftp = self._get_sftp_client(ssh)
            
            try:
                sftp.stat(remote_path)
                return True
            except IOError:
                return False
        except Exception as e:
            logger.error(f"Error checking file existence on VPS: {str(e)}")
            return False
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
    
    def url(self, name):
        """Return URL for accessing the file"""
        # Remove leading slash from name if present
        name = name.lstrip('/')
        # Build full URL
        return urljoin(self.vps_base_url.rstrip('/') + '/', name)
    
    def delete(self, name):
        """Delete file from VPS"""
        ssh = None
        sftp = None
        
        try:
            remote_path = os.path.join(self.vps_base_path, name).replace('\\', '/')
            ssh = self._get_ssh_client()
            sftp = self._get_sftp_client(ssh)
            
            sftp.remove(remote_path)
            logger.info(f"File deleted from VPS: {remote_path}")
        except Exception as e:
            logger.error(f"Failed to delete file from VPS: {str(e)}")
            raise
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
    
    def size(self, name):
        """Get file size from VPS"""
        ssh = None
        sftp = None
        
        try:
            remote_path = os.path.join(self.vps_base_path, name).replace('\\', '/')
            ssh = self._get_ssh_client()
            sftp = self._get_sftp_client(ssh)
            
            stat = sftp.stat(remote_path)
            return stat.st_size
        except Exception as e:
            logger.error(f"Error getting file size from VPS: {str(e)}")
            return 0
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

