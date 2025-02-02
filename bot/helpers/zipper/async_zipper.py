import asyncio
import aiofiles
import zipfile
from pathlib import Path
from typing import List, Optional
from bot.config import Config
from bot.logger import LOGGER

class AsyncZipper:
    def __init__(self):
        self.chunk_size = Config.ZIP_SETTINGS['CHUNK_SIZE']
        self.max_size = Config.ZIP_SETTINGS['MAX_SIZE']
        self._compress_semaphore = asyncio.Semaphore(5)
        self.buffer = []
        self.buffer_size = Config.BUFFER_SIZE
        
    async def _read_file_chunks(self, file_path: str):
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(self.chunk_size):
                yield chunk

    async def create_zip(
        self,
        files: List[str],
        output_path: str,
        split_size: Optional[int] = None
    ) -> List[str]:
        """Create ZIP file with optional splitting and buffering"""
        split_size = split_size or Config.ZIP_SETTINGS['SPLIT_SIZE']
        zip_files = []
        current_zip = 1
        current_size = 0
        
        try:
            async with aiofiles.open(output_path, 'wb') as zip_file:
                with zipfile.ZipFile(
                    zip_file, 
                    'w',
                    compression=zipfile.ZIP_DEFLATED,
                    compresslevel=Config.ZIP_SETTINGS['COMPRESSION_LEVEL']
                ) as zf:
                    for file_path in files:
                        async with self._compress_semaphore:
                            if not Path(file_path).exists():
                                LOGGER.warning(f"File not found: {file_path}")
                                continue
                                
                            file_size = Path(file_path).stat().st_size
                            
                            # Check if need to split
                            if current_size + file_size > split_size:
                                # Flush buffer before starting new file
                                if self.buffer:
                                    await self._write_buffer(zf)
                                
                                zip_files.append(output_path)
                                output_path = f"{output_path}.part{current_zip}"
                                current_zip += 1
                                current_size = 0
                                
                            # Add file to zip with buffering
                            async for chunk in self._read_file_chunks(file_path):
                                self.buffer.append(chunk)
                                current_size += len(chunk)
                                
                                if len(self.buffer) >= self.buffer_size:
                                    await self._write_buffer(zf)
                            
                            # Add remaining buffer content
                            if self.buffer:
                                await self._write_buffer(zf)
                                
            zip_files.append(output_path)
            return zip_files
            
        except Exception as e:
            LOGGER.error(f"ZIP creation failed: {str(e)}")
            raise e

    async def _write_buffer(self, zip_file):
        """Write buffered chunks to zip file"""
        try:
            for chunk in self.buffer:
                zip_file.writestr(
                    f"chunk_{len(self.buffer)}",
                    chunk,
                    compress_type=zipfile.ZIP_DEFLATED
                )
            self.buffer = []
        except Exception as e:
            LOGGER.error(f"Buffer write failed: {str(e)}")
            raise e
