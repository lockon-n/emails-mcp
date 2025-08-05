# Emails MCP Server

A FastMCP-based email management server for IMAP/SMTP operations. This server provides comprehensive email management capabilities through the Model Context Protocol (MCP).

## Features

### Core Email Operations
- **Email Management**: Get, read, search emails with pagination
- **Sending**: Send emails with HTML support, CC/BCC, and attachments
- **Reply & Forward**: Reply to emails (with reply-all option) and forward emails
- **Organization**: Move, delete, and mark emails (read/unread/important)

### Folder Management
- **Folder Operations**: List, create, delete email folders
- **Statistics**: Get mailbox statistics and unread counts

### Draft Management
- **Draft Operations**: Save, update, delete, and list email drafts
- **Persistence**: Drafts are stored locally and can be exported/imported

### Import/Export
- **Backup**: Export emails to JSON format for backup
- **Restore**: Import emails from backup files
- **Attachments**: Download email attachments to specified locations

### Advanced Features
- **Connection Testing**: Check IMAP/SMTP server connectivity
- **Email Headers**: Get complete email headers for technical analysis
- **Batch Operations**: Mark multiple emails, bulk operations support

## Architecture

The project follows a clean layered architecture:

```
- models/          # Data models and configurations
- config/          # Configuration management
- utils/           # Utilities, validators, and parsers
- backends/        # IMAP, SMTP, and file operation backends
- services/        # Business logic layer
- tools/           # MCP tool definitions
- server.py        # Main MCP server entry point
```

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Create email configuration file (`test_emils.json`):
```json
[{
    "email": "your-email@example.com",
    "password": "your-password",
    "name": "Your Name",
    "imap_server": "imap.example.com",
    "imap_port": 993,
    "smtp_server": "smtp.example.com", 
    "smtp_port": 587,
    "use_ssl": true,
    "use_starttls": true
}]
```

## Usage

### Start the MCP Server

```bash
# Basic usage
uv run -m emails_mcp.server

# With custom config file
uv run -m emails_mcp.server --config_file my_emails.json

# With workspace restriction
uv run -m emails_mcp.server --workspace_path /safe/directory

# With debug logging
uv run -m emails_mcp.server --debug
```

### Available MCP Tools

#### Email Operations
- `get_emails(folder, page, page_size)` - Get paginated email list
- `read_email(email_id)` - Read full email content
- `search_emails(query, folder, page, page_size)` - Search emails
- `send_email(to, subject, body, html_body, cc, bcc, attachments)` - Send email
- `reply_email(email_id, body, html_body, cc, bcc, reply_all)` - Reply to email
- `forward_email(email_id, to, body, html_body, cc, bcc)` - Forward email
- `delete_email(email_id)` - Delete email
- `move_email(email_id, target_folder)` - Move email
- `mark_emails(email_ids, status)` - Mark multiple emails

#### Folder Operations
- `get_folders()` - List email folders
- `create_folder(folder_name)` - Create new folder
- `delete_folder(folder_name)` - Delete folder
- `get_mailbox_stats(folder_name)` - Get folder statistics
- `get_unread_count(folder_name)` - Get unread count

#### Management & Utilities
- `check_connection()` - Test server connections
- `get_email_headers(email_id)` - Get complete email headers
- `save_draft(subject, body, html_body, to, cc, bcc)` - Save draft
- `get_drafts(page, page_size)` - List drafts
- `update_draft(draft_id, ...)` - Update existing draft
- `delete_draft(draft_id)` - Delete draft
- `export_emails(folder, export_path)` - Export emails for backup
- `import_emails(import_path, target_folder)` - Import emails
- `download_attachment(email_id, filename, download_path)` - Download attachment

## Configuration

### Email Server Settings
- **IMAP/SMTP servers**: Configure your email provider's servers
- **Security**: Supports SSL/TLS and STARTTLS
- **Authentication**: Standard username/password authentication

### Workspace Security
- **Path Restriction**: Limit file operations to specified directory
- **Path Validation**: All file paths are validated for security

### Pagination
- **Default page size**: 20 items per page
- **Maximum page size**: 50 items per page
- **Auto-correction**: Invalid page parameters are automatically corrected

## Testing

Run the comprehensive test suite:

```bash
# Test individual components
uv run test_config.py
uv run test_utils.py  
uv run test_backends.py
uv run test_services.py

# Run full integration tests
uv run test_integration.py
```

## Error Handling

The server includes comprehensive error handling:
- **Connection errors**: Graceful handling of network issues
- **Authentication errors**: Clear error messages for login failures
- **Validation errors**: Input validation with helpful error messages
- **File system errors**: Proper handling of file operation failures

## Security Considerations

- **Workspace isolation**: File operations can be restricted to a safe directory
- **Input validation**: All user inputs are validated
- **Connection security**: Supports SSL/TLS encryption
- **Error messages**: Avoid exposing sensitive information in error messages

## Development

### Project Structure
The codebase follows software engineering best practices:
- **Separation of concerns**: Clear layer separation
- **Dependency injection**: Services are injected into tools
- **Error handling**: Comprehensive exception handling
- **Testing**: Unit tests for all components
- **Documentation**: Comprehensive docstrings and comments

### Adding New Features
1. Add models in `models/` if needed
2. Implement backend operations in `backends/`  
3. Add business logic in `services/`
4. Create MCP tools in `tools/`
5. Register tools in `server.py`
6. Add tests for new functionality

## License

MIT License