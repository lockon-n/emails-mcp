from typing import List
import logging
from ..models.email import EmailFolder, MailboxStats
from ..backends.imap_backend import IMAPBackend
from ..utils.exceptions import EmailMCPError, FolderError
from ..utils.validators import validate_folder_name


class FolderService:
    """Folder management service layer"""
    
    def __init__(self, imap_backend: IMAPBackend):
        self.imap_backend = imap_backend
    
    def get_folders(self) -> List[EmailFolder]:
        """Get list of all email folders"""
        try:
            return self.imap_backend.list_folders()
        except Exception as e:
            raise EmailMCPError(f"Failed to get folders: {str(e)}")
    
    def create_folder(self, folder_name: str) -> bool:
        """Create new email folder with UTF-8 encoding support"""
        # Validate folder name
        valid, error = validate_folder_name(folder_name)
        if not valid:
            raise FolderError(error)
        
        try:
            self.imap_backend.ensure_connected()
            
            # Try different folder naming conventions with proper UTF-8 encoding
            folder_names_to_try = [
                folder_name,  # Direct name
                f"INBOX.{folder_name}",  # INBOX prefix (common for many servers)
                f"INBOX/{folder_name}",   # INBOX with slash separator
            ]
            
            last_error = None
            for fname in folder_names_to_try:
                try:
                    logging.info(f"Trying to create folder: {fname}")
                    
                    # Handle UTF-8 encoding for Chinese/Unicode folder names
                    if self.imap_backend.utf8_enabled:
                        # Server supports UTF-8, send as UTF-8
                        status, data = self.imap_backend.connection.create(fname)
                    else:
                        # For servers without UTF-8 support, try different encodings
                        try:
                            # Try UTF-7 encoding (IMAP standard for non-ASCII)
                            utf7_fname = fname.encode('utf-7').decode('ascii')
                            status, data = self.imap_backend.connection.create(utf7_fname)
                        except UnicodeError:
                            # If UTF-7 fails, try direct UTF-8
                            status, data = self.imap_backend.connection.create(fname.encode('utf-8'))
                    
                    if status == 'OK':
                        logging.info(f"Successfully created folder: {fname}")
                        return True
                    else:
                        logging.warning(f"Failed to create folder '{fname}': {status} {data}")
                        last_error = f"Server returned: {status} {data}"
                        
                except Exception as e:
                    logging.warning(f"Exception creating folder '{fname}': {e}")
                    last_error = str(e)
            
            # If all attempts failed
            raise FolderError(f"Failed to create folder '{folder_name}' with any naming convention. Last error: {last_error}")
            
        except Exception as e:
            if isinstance(e, FolderError):
                raise
            raise FolderError(f"Failed to create folder: {str(e)}")
    
    def delete_folder(self, folder_name: str) -> bool:
        """Delete email folder"""
        # Validate folder name
        valid, error = validate_folder_name(folder_name)
        if not valid:
            raise FolderError(error)
        
        # Prevent deletion of system folders
        system_folders = ['INBOX', 'Sent', 'Drafts', 'Trash', 'Spam']
        if folder_name in system_folders:
            raise FolderError(f"Cannot delete system folder: {folder_name}")
        
        try:
            self.imap_backend.ensure_connected()
            status, data = self.imap_backend.connection.delete(folder_name)
            
            if status != 'OK':
                raise FolderError(f"Failed to delete folder '{folder_name}': {status}")
            
            return True
            
        except Exception as e:
            raise FolderError(f"Failed to delete folder: {str(e)}")
    
    def get_folder_stats(self, folder_name: str) -> MailboxStats:
        """Get statistics for specific folder"""
        try:
            total_messages, unread_messages = self.imap_backend.select_folder(folder_name)
            
            return MailboxStats(
                folder_name=folder_name,
                total_messages=total_messages,
                unread_messages=unread_messages
            )
            
        except Exception as e:
            raise EmailMCPError(f"Failed to get folder stats: {str(e)}")
    
    def get_unread_count(self, folder_name: str = None) -> int:
        """Get unread message count for folder or all folders"""
        try:
            if folder_name:
                _, unread_count = self.imap_backend.select_folder(folder_name)
                return unread_count
            else:
                # Get unread count for all folders
                folders = self.get_folders()
                total_unread = 0
                for folder in folders:
                    if folder.can_select:
                        total_unread += folder.unread_messages
                return total_unread
                
        except Exception as e:
            raise EmailMCPError(f"Failed to get unread count: {str(e)}")