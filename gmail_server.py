from mcp.server.fastmcp import FastMCP

import json
import re
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.labels"]

# Create an MCP server with a custom name
mcp = FastMCP("Gmail Server")

def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists("/Users/perve/Documents/PythonProjects/MCPServer/token.json"):
        creds = Credentials.from_authorized_user_file("/Users/perve/Documents/PythonProjects/MCPServer/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
            "/Users/perve/Documents/PythonProjects/MCPServer/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("/Users/perve/Documents/PythonProjects/MCPServer/token.json", "w") as token:
            token.write(creds.to_json())
    return creds
    
@mcp.tool()
def get_labels():
    """
    Retrieve all the labels from the user's gmail
    """

    creds = get_credentials()
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            return "No labels found."
        return json.dumps(labels)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        return f"An error occured: {error}"
    

@mcp.tool()
def get_unread():
    """
    Retrieves all of the user's unread emails in their inbox
    """

    creds = get_credentials()

    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=30, labelIds=["INBOX"], q="is:unread").execute()
        messages = results.get("messages", [])

        if not messages:
            return "No messages found."

        messageData = []

        for message in messages:
            messageId = message['id']
            messageResult = service.users().messages().get(userId="me", id=messageId).execute()
            payload = messageResult.get("payload")
            messageData.append(payload)

        return messageData
    except HttpError as error:
        return f"An error occured: {error}"
    

@mcp.tool()
def application_status():
    """
    Retrieves inbox data, then returns entries that might relate to internship applications
    """

    creds = get_credentials()
    messageData = get_unread()

    
    

if __name__ == "__main__":
    mcp.run()