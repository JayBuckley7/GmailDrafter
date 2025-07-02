#!/usr/bin/env python3
"""
Gmail Draft Creator - Simple Version with App Password
Creates Gmail drafts using IMAP with hardcoded credentials
"""

import csv
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List

# HARDCODED CREDENTIALS - CHANGE THESE
GMAIL_EMAIL = "your-email@gmail.com"  # Your Gmail address
GMAIL_APP_PASSWORD = "your-app-password"  # 16-character app password from Google

class SimpleGmailDraftCreator:
    def __init__(self, email_address=GMAIL_EMAIL, app_password=GMAIL_APP_PASSWORD):
        self.email_address = email_address
        self.app_password = app_password
        self.imap = None
        self.connect_imap()
    
    def connect_imap(self):
        """Connect to Gmail via IMAP"""
        try:
            self.imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            self.imap.login(self.email_address, self.app_password)
            print("✅ Successfully connected to Gmail")
        except Exception as e:
            print(f"❌ Failed to connect to Gmail: {e}")
            print("\n🔧 Setup Instructions:")
            print("1. Go to https://myaccount.google.com/security")
            print("2. Enable 2-Factor Authentication")
            print("3. Generate an App Password for 'Mail'")
            print("4. Update GMAIL_EMAIL and GMAIL_APP_PASSWORD in this script")
            raise
    
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
        
        # Replace %name% with actual name
        name = contact.get('name', contact.get('Name', ''))
        processed_template = processed_template.replace('%name%', name)
        
        return processed_template
    
    def create_draft_via_imap(self, to_email: str, subject: str, body: str) -> bool:
        """Create a Gmail draft by appending to Drafts folder"""
        try:
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Convert to string and append to Drafts folder
            raw_email = msg.as_string().encode('utf-8')
            
            # Select Drafts folder and append
            self.imap.select('"[Gmail]/Drafts"')
            self.imap.append('"[Gmail]/Drafts"', '\\Draft', None, raw_email)
            
            print(f"✅ Draft created for {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create draft for {to_email}: {e}")
            return False
    
    def create_drafts_for_contacts(self, template_file='email_template.txt', 
                                 contacts_file='contacts.csv', 
                                 subject_template='Email for %name%'):
        """Main function to create drafts for all contacts"""
        try:
            # Load template and contacts
            template = self.load_template(template_file)
            contacts = self.load_contacts(contacts_file)
            
            print(f"📧 Loaded template from {template_file}")
            print(f"👥 Loaded {len(contacts)} contacts from {contacts_file}")
            print()
            
            # Process each contact
            success_count = 0
            for i, contact in enumerate(contacts, 1):
                name = contact.get('name', contact.get('Name', ''))
                email = contact.get('email', contact.get('Email', ''))
                
                print(f"[{i}/{len(contacts)}] Processing {name}...")
                
                if not email:
                    print(f"⚠️  No email found for {name}")
                    continue
                
                # Process template
                processed_body = self.process_template(template, contact)
                processed_subject = subject_template.replace('%name%', name)
                
                # Create draft
                if self.create_draft_via_imap(email, processed_subject, processed_body):
                    success_count += 1
            
            print(f"\n🎉 Completed! Created {success_count} drafts out of {len(contacts)} contacts.")
            print("📮 Check your Gmail Drafts folder!")
            
        except Exception as e:
            print(f"💥 Error: {e}")
    
    def __del__(self):
        """Close IMAP connection"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass

def main():
    """Main function"""
    print("Gmail Draft Creator - Simple Version")
    print("=" * 50)
    
    # Check if credentials are set
    if GMAIL_EMAIL == "your-email@gmail.com" or GMAIL_APP_PASSWORD == "your-app-password":
        print("❌ Please update the credentials at the top of this script:")
        print("   - GMAIL_EMAIL: Your Gmail address")
        print("   - GMAIL_APP_PASSWORD: Your 16-character app password")
        print("\n🔧 To get an App Password:")
        print("1. Go to https://myaccount.google.com/security")
        print("2. Enable 2-Factor Authentication")
        print("3. Search for 'App passwords'")
        print("4. Generate password for 'Mail'")
        print("5. Copy the 16-character password")
        return 1
    
    try:
        # Initialize the draft creator
        draft_creator = SimpleGmailDraftCreator()
        
        # Create drafts for all contacts
        draft_creator.create_drafts_for_contacts()
        
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 