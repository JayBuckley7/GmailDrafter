# Gmail Draft Creator

Python utility that builds Gmail drafts from a text template and a CSV of contacts.  
Use it when you want personalized emails queued up for manual review before sending.

---

## Features

- OAuth 2.0 authentication with the Gmail API  
- Placeholder-based template rendering (`%name%`, `%email%`, etc.)  
- Reads contacts from a CSV file  
- Creates drafts only—no automatic sending  
- Processes large contact lists in one run  
- Logs progress and errors

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Gmail API Setup

1. Open Google Cloud Console and create or select a project.  
2. Enable **Gmail API** (`APIs & Services → Library`).  
3. Create **OAuth 2.0 Client ID** credentials (type: *Desktop app*).  
4. Download the JSON, rename it to `credentials.json`, and place it beside `main.py`.

---

## Required Files

Copy the example files and customize them:

```bash
cp email_template.txt.example email_template.txt
cp contacts.csv.example contacts.csv
```

### `email_template.txt`

```
Hi %name%,

Your personalized message here.

Best,
Your Name
```

### `contacts.csv`

```csv
name,email
John Smith,john.smith@example.com
Jane Doe,jane.doe@example.com
```

**Note:** The actual `email_template.txt` and `contacts.csv` files are gitignored to protect your personal data.

---

## Running the Script

```bash
python main.py
```

The first run opens a browser window for Gmail consent and stores `token.pickle` for future runs.

---

## File Layout

```
EmailDrafter/
├── main.py
├── requirements.txt
├── credentials.json        # you add this
├── email_template.txt      # copy from .example file
├── contacts.csv           # copy from .example file
├── email_template.txt.example
├── contacts.csv.example
├── token.pickle            # generated at first run
└── README.md
```

---

## Customization

### Extra Placeholders

Edit `process_template` in `main.py` to support additional fields:

```python
processed = template.replace('%company%', contact.get('company', ''))
```

### Subject Line

Override the default subject:

```python
draft_creator.create_drafts_for_contacts(
    template_file='email_template.txt',
    contacts_file='contacts.csv',
    subject_template='Welcome, %name%'
)
```

### Alternate Filenames

```python
draft_creator.create_drafts_for_contacts(
    template_file='my_template.txt',
    contacts_file='team_list.csv'
)
```

---

## Security

The following sensitive files are automatically excluded from version control:
- `credentials.json` - Gmail API credentials
- `token.pickle` - OAuth tokens  
- `contacts.csv` - Your personal contact list
- `email_template.txt` - Your personalized template

Use the `.example` files as templates to create your own versions.

---

## Troubleshooting

| Issue                                  | Fix                                                                           |
|----------------------------------------|-------------------------------------------------------------------------------|
| `credentials.json` not found           | Verify the file name and location.                                            |
| `email_template.txt` missing           | Create the template and include `%name%` or other placeholders.               |
| `contacts.csv` missing                 | Supply a CSV with `name` and `email` columns.                                 |
| Auth errors                            | Delete `token.pickle`, re-run the script, and confirm Gmail API is enabled.   |

---

## License

MIT License
