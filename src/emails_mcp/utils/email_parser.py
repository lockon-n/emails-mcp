import email
import email.message
import logging
from email.header import decode_header
from email.utils import parseaddr, formataddr
from typing import Dict, Any, List, Optional
from ..models.email import EmailMessage, EmailAttachment
from .exceptions import ValidationError


def decode_email_header(header_value: str) -> str:
    """Decode email header properly handling encoding"""
    if header_value is None:
        return ""
    
    try:
        decoded_parts = decode_header(header_value)
        result = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    result += part.decode(encoding, errors='ignore')
                else:
                    result += part.decode('utf-8', errors='ignore')
            else:
                result += str(part)
        return result.strip()
    except Exception as e:
        logging.warning(f"Failed to decode header: {str(e)}")
        return str(header_value)


def parse_email_addresses(addr_string: str) -> List[str]:
    """Parse comma-separated email addresses"""
    if not addr_string:
        return []
    
    addresses = []
    for addr in addr_string.split(','):
        addr = addr.strip()
        if addr:
            # Extract just the email part if in "Name <email>" format
            _, email_addr = parseaddr(addr)
            if email_addr:
                addresses.append(email_addr)
            else:
                addresses.append(addr)
    
    return addresses


def extract_attachments_info(msg: email.message.Message) -> List[EmailAttachment]:
    """Extract attachment information from email message"""
    attachments = []
    
    if not msg.is_multipart():
        return attachments
    
    for part in msg.walk():
        disposition = part.get('Content-Disposition', '')
        if 'attachment' in disposition:
            filename = part.get_filename()
            if filename:
                # Decode filename if needed
                filename = decode_email_header(filename)
                
                # Get content info
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)
                size = len(payload) if payload else 0
                
                attachment = EmailAttachment(
                    filename=filename,
                    content_type=content_type,
                    size=size
                )
                attachments.append(attachment)
    
    return attachments


def extract_email_body(msg: email.message.Message) -> tuple[str, str]:
    """Extract text and HTML body from email message"""
    body_text = ""
    body_html = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = part.get('Content-Disposition', '')
            
            # Skip attachments
            if 'attachment' in disposition:
                continue
                
            payload = part.get_payload(decode=True)
            if not payload:
                continue
                
            try:
                content = payload.decode('utf-8', errors='ignore')
            except:
                continue
                
            if content_type == 'text/plain' and not body_text:
                body_text = content
            elif content_type == 'text/html' and not body_html:
                body_html = content
    else:
        # Single part message
        payload = msg.get_payload(decode=True)
        if payload:
            try:
                content = payload.decode('utf-8', errors='ignore')
                if msg.get_content_type() == 'text/html':
                    body_html = content
                else:
                    body_text = content
            except:
                pass
    
    return body_text, body_html


def parse_raw_email(raw_email: bytes, email_id: str) -> EmailMessage:
    """Parse raw email bytes into EmailMessage object"""
    try:
        msg = email.message_from_bytes(raw_email)
        
        # Extract headers
        subject = decode_email_header(msg.get('Subject', ''))
        from_addr = decode_email_header(msg.get('From', ''))
        to_addr = decode_email_header(msg.get('To', ''))
        cc_addr = decode_email_header(msg.get('Cc', '')) or None
        date = msg.get('Date', '')
        message_id = msg.get('Message-ID', '')
        
        # Extract body content
        body_text, body_html = extract_email_body(msg)
        
        # Extract attachments
        attachments = extract_attachments_info(msg)
        
        return EmailMessage(
            email_id=email_id,
            subject=subject,
            from_addr=from_addr,
            to_addr=to_addr,
            cc_addr=cc_addr,
            date=date,
            message_id=message_id,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            raw_message=msg
        )
        
    except Exception as e:
        logging.error(f"Failed to parse email {email_id}: {str(e)}")
        raise ValidationError(f"Failed to parse email: {str(e)}")


def format_email_summary(email: EmailMessage, include_body_preview: bool = False) -> str:
    """Format email for display summary"""
    result = f"Subject: {email.subject}\n"
    result += f"From: {email.from_addr}\n"
    result += f"To: {email.to_addr}\n"
    
    if email.cc_addr:
        result += f"CC: {email.cc_addr}\n"
    
    result += f"Date: {email.date}\n"
    
    if email.attachments:
        result += f"Attachments: {len(email.attachments)} files\n"
    
    if include_body_preview and email.body_text:
        preview = email.body_text[:200] + "..." if len(email.body_text) > 200 else email.body_text
        result += f"Preview: {preview}\n"
    
    return result