import asyncio
import aiofiles
import zipfile
from pathlib import Path
from typing import List, Optional
from bot.config import Config

class AsyncZipper:
    def __init__(self):
        self.chunk_size = Config.ZIP_SETTINGS['CHUNK_SIZE']
        self.max_size = Config.ZIP_SETTINGS['MAX_SIZE']
        self._compress_semaphore = asyncio.Semaphore(5)
        
    async def create_zip(
        self,
        files: List[str],
        output_path: str,
        split_size: Optional[int] = None
    ) -> List[str]:
        """Create ZIP file with optional splitting"""
        split_size = split_size or self.max_size
        zip_files = []
        current_zip = 1
        current_size = 0
        
        async with aiofiles.open(output_path, 'wb') as zip_file:
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in files:
                    async with self._compress_semaphore:
                        file_size = Path(file_path).stat().st_size
                        
                        # Check if need to split
                        if current_size + file_size > split_size:
                            zip_files.append(output_path)
                            output_path = f"{output_path}.part{current_zip}"
                            current_zip += 1
                            current_size = 0
                            
                        # Add file to zip
                        zf.write(
                            file_path,
                            arcname=Path(file_path).name
                        )
                        current_size += file_size
                        
        zip_files.append(output_path)
        return zip_files
