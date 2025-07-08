import os
import shutil
from pathlib import Path
import logging
from collections import defaultdict

class FileOrganizer:
    def __init__(self, source_directory=None):
        # Default to Downloads folder if no directory specified
        self.source_directory = source_directory or str(Path.home() / "Downloads")
        
        # Define file type categories and their extensions
        self.file_categories = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
            'Videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
            'Executables': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.app'],
            'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'Presentations': ['.ppt', '.pptx', '.odp'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go'],
            'Ebooks': ['.epub', '.mobi', '.azw', '.azw3']
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('file_organizer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_file_category(self, file_extension):
        """Determine the category of a file based on its extension."""
        file_extension = file_extension.lower()
        for category, extensions in self.file_categories.items():
            if file_extension in extensions:
                return category
        return 'Others'  # Default category for unrecognized extensions

    def create_directories(self):
        """Create category directories if they don't exist."""
        categories = list(self.file_categories.keys()) + ['Others']
        created_dirs = []
        
        for category in categories:
            category_path = os.path.join(self.source_directory, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
                created_dirs.append(category)
                self.logger.info(f"Created directory: {category}")
        
        return created_dirs

    def organize_files(self, dry_run=False):
        """Organize files in the source directory."""
        if not os.path.exists(self.source_directory):
            self.logger.error(f"Source directory does not exist: {self.source_directory}")
            return False

        # Get all files in the source directory (excluding subdirectories)
        files = [f for f in os.listdir(self.source_directory) 
                if os.path.isfile(os.path.join(self.source_directory, f))]
        
        if not files:
            self.logger.info("No files found to organize.")
            return True

        # Create necessary directories
        if not dry_run:
            self.create_directories()

        # Statistics tracking
        stats = defaultdict(int)
        moved_files = []
        errors = []

        for filename in files:
            try:
                file_path = os.path.join(self.source_directory, filename)
                file_extension = Path(filename).suffix
                
                # Skip hidden files and system files
                if filename.startswith('.') or filename.startswith('~'):
                    continue
                
                category = self.get_file_category(file_extension)
                destination_dir = os.path.join(self.source_directory, category)
                destination_path = os.path.join(destination_dir, filename)
                
                # Handle file name conflicts
                counter = 1
                original_destination = destination_path
                while os.path.exists(destination_path):
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}_{counter}{ext}"
                    destination_path = os.path.join(destination_dir, new_filename)
                    counter += 1
                
                if dry_run:
                    self.logger.info(f"[DRY RUN] Would move: {filename} -> {category}/")
                else:
                    shutil.move(file_path, destination_path)
                    moved_files.append((filename, category))
                    self.logger.info(f"Moved: {filename} -> {category}/")
                
                stats[category] += 1
                
            except Exception as e:
                error_msg = f"Error processing {filename}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)

        # Print summary
        self.print_summary(stats, moved_files, errors, dry_run)
        return len(errors) == 0

    def print_summary(self, stats, moved_files, errors, dry_run=False):
        """Print a summary of the organization process."""
        action = "Would be moved" if dry_run else "Moved"
        
        print("\n" + "="*50)
        print(f"FILE ORGANIZATION SUMMARY {'(DRY RUN)' if dry_run else ''}")
        print("="*50)
        
        total_files = sum(stats.values())
        print(f"Total files processed: {total_files}")
        
        if stats:
            print("\nFiles by category:")
            for category, count in sorted(stats.items()):
                print(f"  {category}: {count} files")
        
        if errors:
            print(f"\nErrors encountered: {len(errors)}")
            for error in errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more errors")
        
        print("="*50)

    def undo_organization(self):
        """Move all files back to the root directory (undo organization)."""
        categories = list(self.file_categories.keys()) + ['Others']
        moved_count = 0
        
        for category in categories:
            category_path = os.path.join(self.source_directory, category)
            if os.path.exists(category_path) and os.path.isdir(category_path):
                files = os.listdir(category_path)
                for filename in files:
                    try:
                        source = os.path.join(category_path, filename)
                        destination = os.path.join(self.source_directory, filename)
                        
                        # Handle conflicts
                        counter = 1
                        while os.path.exists(destination):
                            name, ext = os.path.splitext(filename)
                            new_filename = f"{name}_restored_{counter}{ext}"
                            destination = os.path.join(self.source_directory, new_filename)
                            counter += 1
                        
                        shutil.move(source, destination)
                        moved_count += 1
                        self.logger.info(f"Restored: {filename}")
                        
                    except Exception as e:
                        self.logger.error(f"Error restoring {filename}: {str(e)}")
                
                # Remove empty directory
                try:
                    if not os.listdir(category_path):
                        os.rmdir(category_path)
                        self.logger.info(f"Removed empty directory: {category}")
                except:
                    pass
        
        print(f"Restored {moved_count} files to the root directory.")

def main():
    """Main function with command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize files by extension into categories")
    parser.add_argument("--directory", "-d", help="Directory to organize (default: Downloads)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without actually moving files")
    parser.add_argument("--undo", action="store_true", help="Undo previous organization")
    
    args = parser.parse_args()
    
    # Create organizer instance
    organizer = FileOrganizer(args.directory)
    
    print(f"File Organizer - Target Directory: {organizer.source_directory}")
    
    if args.undo:
        print("Undoing previous organization...")
        organizer.undo_organization()
    elif args.dry_run:
        print("Running in DRY RUN mode (no files will be moved)...")
        organizer.organize_files(dry_run=True)
    else:
        print("Organizing files...")
        success = organizer.organize_files()
        if success:
            print("Organization completed successfully!")
        else:
            print("Organization completed with some errors. Check the log for details.")

if __name__ == "__main__":
    main()