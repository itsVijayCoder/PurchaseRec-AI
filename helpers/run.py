import tempfile, os

def run_file_generation(file, isProposal=False):
    try:
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            temp_file_path = os.path.join(temp_dir, file.filename)
            if isProposal: 
                filename = file.filename.split('/')[-1]
                temp_file_path = os.path.join(temp_dir, filename)
            with open(temp_file_path, 'wb') as temp_file:
                content = file.file.read()
                temp_file.write(content)
                
        return temp_file_path
        
    except Exception as e:
        print(f"Error generating temp file: {e}")

def run_file_deletion(file_path):
    try:
        os.remove(file_path)
        return True

    except FileNotFoundError as e:
        print(f"Error deleting temp file: {e}")
        return False