import tempfile, os

async def run_temp_file_generation(file):

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file.filename)

        with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
            content = await file.read()
            temp_file.write(content)

    return temp_file_path

async def run_temp_file_deletion(file_path):
    try:
        os.remove(file_path)
        return True

    except FileNotFoundError as e:
        print(f"Error deleting temp file: {e}")
        return False