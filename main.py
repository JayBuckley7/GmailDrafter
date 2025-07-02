#!/usr/bin/env python3
"""
Gmail Draft Creator
Creates Gmail drafts from a template for a list of contacts
"""

import os
import json
import csv
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pickle

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

class GmailDraftCreator:
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Credentials file '{self.credentials_file}' not found. Please download it from Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("Successfully authenticated with Gmail API")
    
    def load_template(self, template_file='email_template.txt'):
        """Load email template from file"""
        try:
            with open(template_file, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file '{template_file}' not found")
    
    def load_contacts(self, contacts_file='contacts.csv'):
        """Load contacts from CSV file"""
        contacts = []
        try:
            with open(contacts_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    contacts.append(row)
            return contacts
        except FileNotFoundError:
            raise FileNotFoundError(f"Contacts file '{contacts_file}' not found")
    
    def process_template(self, template: str, contact: Dict) -> str:
        """Replace placeholders in template with contact information"""
        processed_template = template
        
        # Replace %name% with first name only
        full_name = contact.get('name', contact.get('Name', ''))
        first_name = full_name.split()[0] if full_name else ''
        processed_template = processed_template.replace('%name%', first_name)
        
        # You can add more replacements here for other fields
        # processed_template = processed_template.replace('%email%', contact.get('email', ''))
        # processed_template = processed_template.replace('%company%', contact.get('company', ''))
        
        return processed_template
    
    def convert_to_html(self, text: str) -> str:
        """Convert plain text email to HTML with clickable links"""
        import re
        
        # Replace line breaks with <br> tags
        html = text.replace('\n', '<br>\n')
        
        # Convert URLs to clickable links
        url_pattern = r'(https?://[^\s<>"]+)'
        html = re.sub(url_pattern, r'<a href="\1">\1</a>', html)
        
        return f"""
        <html>
        <body>
        {html}
        </body>
        </html>
        """
    
    def create_draft(self, to_email: str, subject: str, body: str) -> bool:
        """Create a Gmail draft"""
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            
            # Convert links to HTML and add body
            html_body = self.convert_to_html(body)
            message.attach(MIMEText(html_body, 'html'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Create draft
            draft = {
                'message': {
                    'raw': raw_message
                }
            }
            
            result = self.service.users().drafts().create(userId='me', body=draft).execute()
            print(f"Draft created successfully for {to_email} (ID: {result['id']})")
            return True
            
        except HttpError as error:
            print(f"An error occurred creating draft for {to_email}: {error}")
            return False
    
    def create_drafts_for_contacts(self, template_file='email_template.txt', 
                                 contacts_file='contacts.csv', 
                                 subject_template='Faeling Facture pet commission information'):
        """Main function to create drafts for all contacts"""
        try:
            # Load template and contacts
            template = self.load_template(template_file)
            contacts = self.load_contacts(contacts_file)
            
            print(f"Loaded template from {template_file}")
            print(f"Loaded {len(contacts)} contacts from {contacts_file}")
            
            # Process each contact
            success_count = 0
            for contact in contacts:
                name = contact.get('name', contact.get('Name', ''))
                email = contact.get('email', contact.get('Email', ''))
                
                if not email:
                    print(f"Warning: No email found for contact {name}")
                    continue
                
                # Process template
                processed_body = self.process_template(template, contact)
                processed_subject = subject_template.replace('%name%', name)
                
                # Create draft
                if self.create_draft(email, processed_subject, processed_body):
                    success_count += 1
            
            print(f"\nCompleted! Created {success_count} drafts out of {len(contacts)} contacts.")
            
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function"""
    print("Gmail Draft Creator")
    print("=" * 50)
    
    try:
        # Initialize the draft creator
        draft_creator = GmailDraftCreator()
        
        # Create drafts for all contacts
        draft_creator.create_drafts_for_contacts()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 