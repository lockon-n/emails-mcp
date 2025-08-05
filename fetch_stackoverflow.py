#!/usr/bin/env python3
"""
Fetch StackOverflow solution for Chinese IMAP search
"""
import requests
from bs4 import BeautifulSoup
import re

def fetch_stackoverflow_solution():
    """Fetch the StackOverflow solution for Chinese IMAP search"""
    url = "https://stackoverflow.com/questions/48981299/python-imaplib-search-email-subject-chinese-got-error"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the question
        question_div = soup.find('div', class_='postcell')
        if question_div:
            print("QUESTION:")
            print("=" * 50)
            question_text = question_div.get_text(strip=True)
            print(question_text[:500] + "...")
        
        # Find all answers
        answers = soup.find_all('div', class_='answercell')
        
        for i, answer in enumerate(answers):
            print(f"\nANSWER {i+1}:")
            print("=" * 50)
            
            # Get answer text
            answer_text = answer.get_text(strip=True)
            print(answer_text[:800] + "...")
            
            # Look for code blocks
            code_blocks = answer.find_all('code')
            if code_blocks:
                print("\nCODE EXAMPLES:")
                for j, code in enumerate(code_blocks):
                    code_text = code.get_text()
                    if len(code_text) > 10:  # Skip short inline code
                        print(f"Code {j+1}: {code_text}")
        
        return True
        
    except Exception as e:
        print(f"Error fetching StackOverflow: {str(e)}")
        return False

if __name__ == "__main__":
    fetch_stackoverflow_solution()