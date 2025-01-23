from mega import Mega
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

class MegaHandler:
    def __init__(self, email: str, password: str):
        self.mega = Mega()
        self.m = self.mega.login(email, password)
        self.files = []
        self.renamed_count = 0
        self.failed_count = 0
        self.error_messages = []

    def get_all_files(self) -> List[Dict]:
        """Get all files from Mega account."""
        files = []
        all_items = self.m.get_files()

        for file_id, file_info in all_items.items():
            if 'a' in file_info:  # Only add files, skip folders
                files.append(file_info)
        return files

    def rename_file_with_retry(self, file_info: Dict, file_number: int, retries: int = 3) -> None:
        """Rename a single file with retry mechanism."""
        original_file_name = file_info['a']['n']
        new_name = f"@ Telegram {file_number}{original_file_name[original_file_name.rfind('.'):]}"

        for attempt in range(retries):
            try:
                file = self.m.find(original_file_name)
                if file:
                    self.m.rename(file, new_name)
                    self.renamed_count += 1
                    return
                else:
                    self.failed_count += 1
                    self.error_messages.append(f"File '{original_file_name}' not found.")
                    return
            except Exception as e:
                if attempt == retries - 1:
                    self.failed_count += 1
                    self.error_messages.append(f"Failed to rename '{original_file_name}': {str(e)}")
                time.sleep(2)

    def rename_all_files(self) -> str:
        """Rename all files in the Mega account."""
        self.files = self.get_all_files()
        self.renamed_count = 0
        self.failed_count = 0
        self.error_messages = []

        if not self.files:
            return "No files found in your Mega account."

        with ThreadPoolExecutor(max_workers=20) as executor:
            for file_number, file_info in enumerate(self.files, start=1):
                executor.submit(self.rename_file_with_retry, file_info, file_number)

        # Prepare result message
        result = f"📊 Rename Statistics:\n"
        result += f"✅ Successfully renamed: {self.renamed_count}\n"
        result += f"❌ Failed: {self.failed_count}\n"
        
        if self.error_messages:
            result += "\n⚠️ Errors:\n"
            result += "\n".join(self.error_messages[:5])  # Show first 5 errors
            if len(self.error_messages) > 5:
                result += f"\n... and {len(self.error_messages) - 5} more errors"

        return result