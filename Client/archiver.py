import os
import shutil


class Archiver:
    def __init__(self, archive_dir='archive'):
        self.archive_dir = archive_dir
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def archive_directory(self, source_dir):
        """Archives a directory by moving it into the archive directory."""
        try:
            # Generate a unique name for the archive directory
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{os.path.basename(source_dir)}_{timestamp}"
            destination_dir = os.path.join(self.archive_dir, archive_name)

            # Move the directory
            shutil.move(source_dir, destination_dir)
            print(f"Directory '{source_dir}' archived to '{destination_dir}'")
            return destination_dir
        except Exception as e:
            print(f"Error archiving directory '{source_dir}': {e}")
            return None

    def restore_directory(self, archive_path, destination_dir):
        """Restores a directory from the archive."""
        try:
            # Move the directory back
            shutil.move(archive_path, destination_dir)
            print(f"Directory '{archive_path}' restored to '{destination_dir}'")
            return destination_dir
        except Exception as e:
            print(f"Error restoring directory '{archive_path}': {e}")
            return None
