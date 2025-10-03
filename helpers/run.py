import tempfile, os, shutil

def run_file_generation(file, isProposal=False):
    try:
        # Create a temporary directory that will be automatically cleaned up
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create the file path
            if isProposal: 
                filename = file.filename.split('/')[-1]
            else:
                filename = file.filename
                
            temp_file_path = os.path.join(temp_dir, filename)
            
            # Write the file content
            with open(temp_file_path, 'wb') as temp_file:
                content = file.read()
                temp_file.write(content)
                
            return temp_file_path
        except Exception as e:
            # Clean up on error
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e
                
    except Exception as e:
        print(f"Error generating temp file: {e}")
        return None

def run_file_deletion(file_path):
    if file_path is None:
        print("Warning: Attempted to delete None file path")
        return False
        
    try:
        # Remove the file
        os.remove(file_path)
        
        # Also remove the parent directory if it's empty
        parent_dir = os.path.dirname(file_path)
        if os.path.exists(parent_dir) and not os.listdir(parent_dir):
            try:
                os.rmdir(parent_dir)
            except Exception as dir_error:
                print(f"Warning: Could not remove temp directory: {dir_error}")
        
        return True

    except Exception as e:
        print(f"Error deleting temp file: {e}")
        return False