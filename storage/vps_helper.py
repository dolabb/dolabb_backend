"""
Helper functions for VPS file operations
Simplified interface for uploading files to VPS
"""
import os
import paramiko
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def upload_file_to_vps(file_content, remote_path, file_name=None):
    """
    Upload file to VPS via SFTP
    
    Args:
        file_content: Bytes content of the file
        remote_path: Remote directory path (e.g., 'uploads/profiles')
        file_name: Name of the file (if None, will be generated)
    
    Returns:
        tuple: (success: bool, file_url: str or error_message: str)
    """
    vps_host = getattr(settings, 'VPS_HOST', None)
    vps_port = getattr(settings, 'VPS_PORT', 22)
    vps_username = getattr(settings, 'VPS_USERNAME', None)
    vps_password = getattr(settings, 'VPS_PASSWORD', None)
    vps_key_path = getattr(settings, 'VPS_KEY_PATH', None)
    vps_base_path = getattr(settings, 'VPS_BASE_PATH', '/var/www/media')
    vps_base_url = getattr(settings, 'VPS_BASE_URL', None)
    
    if not all([vps_host, vps_username, vps_base_url]):
        return False, "VPS configuration is incomplete. Please set VPS_HOST, VPS_USERNAME, and VPS_BASE_URL in settings."
    
    ssh = None
    sftp = None
    
    try:
        # Generate filename if not provided
        if not file_name:
            import uuid
            file_name = f"{uuid.uuid4()}.jpg"
        
        # Build full remote path
        full_remote_path = os.path.join(vps_base_path, remote_path, file_name).replace('\\', '/')
        remote_dir = os.path.dirname(full_remote_path)
        
        # Connect to VPS
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if vps_key_path and os.path.exists(vps_key_path):
                logger.info(f"Attempting SSH connection to {vps_host}:{vps_port} with key file")
                ssh.connect(vps_host, port=vps_port, username=vps_username, key_filename=vps_key_path, timeout=30)
            elif vps_password:
                logger.info(f"Attempting SSH connection to {vps_host}:{vps_port} with password")
                ssh.connect(vps_host, port=vps_port, username=vps_username, password=vps_password, timeout=30)
            else:
                return False, "Either VPS_PASSWORD or VPS_KEY_PATH must be set"
            logger.info(f"SSH connection successful to {vps_host}")
        except paramiko.AuthenticationException as e:
            error_msg = f"VPS Authentication failed: {str(e)}. Check VPS_USERNAME and VPS_PASSWORD/VPS_KEY_PATH"
            logger.error(error_msg)
            return False, error_msg
        except paramiko.SSHException as e:
            error_msg = f"VPS SSH connection error: {str(e)}. Check VPS_HOST ({vps_host}) and network connectivity"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"VPS connection failed: {str(e)}. Check VPS_HOST, VPS_PORT, and network connectivity"
            logger.error(error_msg)
            return False, error_msg
        
        sftp = ssh.open_sftp()
        
        # Ensure directory exists
        try:
            sftp.stat(remote_dir)
            logger.info(f"Directory exists: {remote_dir}")
        except IOError:
            # Create directory structure
            logger.info(f"Creating directory structure: {remote_dir}")
            parts = remote_dir.strip('/').split('/')
            current_path = ''
            for part in parts:
                if current_path:
                    current_path = f"{current_path}/{part}"
                else:
                    current_path = f"/{part}"
                try:
                    sftp.stat(current_path)
                except IOError:
                    try:
                        sftp.mkdir(current_path)
                        logger.info(f"Created directory: {current_path}")
                    except Exception as e:
                        error_msg = f"Failed to create directory {current_path}: {str(e)}. Check permissions on VPS"
                        logger.error(error_msg)
                        return False, error_msg
        
        # Write file
        try:
            logger.info(f"Writing file to VPS: {full_remote_path}")
            with sftp.open(full_remote_path, 'wb') as remote_file:
                remote_file.write(file_content)
            logger.info(f"File written successfully: {full_remote_path}")
        except IOError as e:
            error_msg = f"Failed to write file to VPS: {str(e)}. Check directory permissions on VPS ({remote_dir})"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to write file to VPS: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        
        # Build URL - ensure proper formatting
        # Remove trailing slashes and ensure single slash between parts
        base_url = vps_base_url.rstrip('/')
        remote_path_clean = remote_path.strip('/')
        file_url = f"{base_url}/{remote_path_clean}/{file_name}"
        
        logger.info(f"File uploaded to VPS: {full_remote_path}, URL: {file_url}")
        return True, file_url
        
    except paramiko.AuthenticationException as e:
        error_msg = f"VPS Authentication failed: {str(e)}. Check VPS_USERNAME and VPS_PASSWORD/VPS_KEY_PATH"
        logger.error(error_msg)
        return False, error_msg
    except paramiko.SSHException as e:
        error_msg = f"VPS SSH connection error: {str(e)}. Check VPS_HOST and network connectivity"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Failed to upload file to VPS: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, error_msg
    finally:
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()


def delete_file_from_vps(remote_path):
    """
    Delete file from VPS
    
    Args:
        remote_path: Full remote path to the file
    
    Returns:
        bool: True if successful, False otherwise
    """
    vps_host = getattr(settings, 'VPS_HOST', None)
    vps_port = getattr(settings, 'VPS_PORT', 22)
    vps_username = getattr(settings, 'VPS_USERNAME', None)
    vps_password = getattr(settings, 'VPS_PASSWORD', None)
    vps_key_path = getattr(settings, 'VPS_KEY_PATH', None)
    vps_base_path = getattr(settings, 'VPS_BASE_PATH', '/var/www/media')
    
    if not all([vps_host, vps_username]):
        return False
    
    ssh = None
    sftp = None
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if vps_key_path and os.path.exists(vps_key_path):
            ssh.connect(vps_host, port=vps_port, username=vps_username, key_filename=vps_key_path, timeout=10)
        elif vps_password:
            ssh.connect(vps_host, port=vps_port, username=vps_username, password=vps_password, timeout=10)
        else:
            return False
        
        sftp = ssh.open_sftp()
        sftp.remove(remote_path)
        logger.info(f"File deleted from VPS: {remote_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete file from VPS: {str(e)}")
        return False
    finally:
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()

