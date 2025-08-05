import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.models.config import EmailConfig
from emails_mcp.services import DraftService
from emails_mcp.backends import FileBackend
import tempfile

def test_draft_service():
    """Test draft service operations"""
    print("Testing DraftService...")
    
    # Create service with file backend
    with tempfile.TemporaryDirectory() as temp_dir:
        file_backend = FileBackend(temp_dir)
        draft_service = DraftService(file_backend)
        
        # Test save draft
        draft_id = draft_service.save_draft(
            subject="Test Draft",
            body="Test draft body",
            to="recipient@example.com"
        )
        assert draft_id is not None
        print("✓ Save draft works")
        
        # Test get drafts
        drafts_result = draft_service.get_drafts()
        assert drafts_result['total_drafts'] == 1
        assert len(drafts_result['drafts']) == 1
        assert drafts_result['drafts'][0]['subject'] == "Test Draft"
        print("✓ Get drafts works")
        
        # Test get specific draft
        draft = draft_service.get_draft(draft_id)
        assert draft['subject'] == "Test Draft"
        assert draft['body'] == "Test draft body"
        assert draft['to'] == "recipient@example.com"
        print("✓ Get specific draft works")
        
        # Test update draft
        success = draft_service.update_draft(
            draft_id,
            subject="Updated Draft",
            cc="cc@example.com"
        )
        assert success == True
        
        updated_draft = draft_service.get_draft(draft_id)
        assert updated_draft['subject'] == "Updated Draft"
        assert updated_draft['cc'] == "cc@example.com"
        assert updated_draft['body'] == "Test draft body"  # Unchanged
        print("✓ Update draft works")
        
        # Test delete draft
        success = draft_service.delete_draft(draft_id)
        assert success == True
        
        drafts_result = draft_service.get_drafts()
        assert drafts_result['total_drafts'] == 0
        print("✓ Delete draft works")


def test_draft_pagination():
    """Test draft pagination"""
    print("Testing draft pagination...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_backend = FileBackend(temp_dir)
        draft_service = DraftService(file_backend)
        
        # Create multiple drafts
        for i in range(5):
            draft_service.save_draft(
                subject=f"Draft {i+1}",
                body=f"Body {i+1}",
                to="test@example.com"
            )
        
        # Test pagination
        page1 = draft_service.get_drafts(page=1, page_size=2)
        assert len(page1['drafts']) == 2
        assert page1['total_drafts'] == 5
        assert page1['total_pages'] == 3
        assert page1['current_page'] == 1
        print("✓ Draft pagination works")


def test_draft_errors():
    """Test draft error handling"""
    print("Testing draft error handling...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_backend = FileBackend(temp_dir)
        draft_service = DraftService(file_backend)
        
        # Test get non-existent draft
        try:
            draft_service.get_draft("nonexistent")
            assert False, "Should have raised error"
        except Exception as e:
            assert "not found" in str(e)
        
        # Test update non-existent draft
        try:
            draft_service.update_draft("nonexistent", subject="test")
            assert False, "Should have raised error"
        except Exception as e:
            assert "not found" in str(e)
        
        print("✓ Draft error handling works")


if __name__ == "__main__":
    test_draft_service()
    test_draft_pagination()
    test_draft_errors()
    print("All service tests passed!")