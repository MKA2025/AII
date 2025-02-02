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
        self._memory_pool = []
        self._max_memory = Config.PERFORMANCE['MEMORY_LIMIT']
        self._progress_callback = None
        
    async def validate_files(self, files: List[str]) -> bool:
        """Validate files before zipping"""
        try:
            total_size = 0
            for file_path in files:
                if not Path(file_path).exists():
                    LOGGER.error(f"File not found: {file_path}")
                    continue
                    
                if Path(file_path).suffix.lower() not in Config.ZIP_SETTINGS['ALLOWED_TYPES']:
                    LOGGER.warning(f"Skipping unsupported file: {file_path}")
                    continue
                    
                file_size = Path(file_path).stat().st_size
                if file_size > Config.SECURITY['MAX_FILE_SIZE']:
                    LOGGER.warning(f"File too large, will be split: {file_path}")
                    
                total_size += file_size
                
            return total_size <= self.max_size
            
        except Exception as e:
            LOGGER.error(f"File validation failed: {str(e)}")
            return False

    async def _read_file_chunks(self, file_path: str):
        """Read file in chunks"""
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(self.chunk_size):
                yield chunk

    async def _check_memory(self, size: int) -> bool:
        """Check memory availability"""
        current_usage = sum(len(item) for item in self._memory_pool)
        return (current_usage + size) <= self._max_memory

    async def _clear_memory(self):
        """Clear memory pool"""
        while self._memory_pool:
            self._memory_pool.pop()

    async def create_zip(
        self,
        files: List[str],
        output_path: str,
        split_size: Optional[int] = None,
        message = None
    ) -> List[str]:
        """Create ZIP file with memory management and progress tracking"""
        split_size = split_size or Config.ZIP_SETTINGS['SPLIT_SIZE']
        zip_files = []
        current_zip = 1
        current_size = 0
        
        try:
            # Validate files first
            if not await self.validate_files(files):
                raise ValueError("File validation failed")
            
            async with aiofiles.open(output_path, 'wb') as zip_file:
                with zipfile.ZipFile(
                    zip_file, 
                    'w',
                    compression=zipfile.ZIP_DEFLATED,
                    compresslevel=Config.ZIP_SETTINGS['COMPRESSION_LEVEL']
                ) as zf:
                    total_size = sum(Path(f).stat().st_size for f in files)
                    processed_size = 0
                    start_time = asyncio.get_event_loop().time()
                    
                    for file_path in files:
                        async with self._compress_semaphore:
                            if not Path(file_path).exists():
                                LOGGER.warning(f"File not found: {file_path}")
                                continue
                                
                            file_size = Path(file_path).stat().st_size
                            
                            # Check if need to split
                            if current_size + file_size > split_size:
                                zip_files.append(output_path)
                                output_path = f"{output_path}.part{current_zip}"
                                current_zip += 1
                                current_size = 0
                                
                            # Add file to zip
                            current_file_size = 0
                            async for chunk in self._read_file_chunks(file_path):
                                if not await self._check_memory(len(chunk)):
                                    await self._clear_memory()
                                    
                                self._memory_pool.append(chunk)
                                current_size += len(chunk)
                                current_file_size += len(chunk)
                                processed_size += len(chunk)
                                
                                # Update progress
                                if message and (asyncio.get_event_loop().time() - start_time) >= Config.PERFORMANCE['PROGRESS_UPDATE_DELAY']:
                                    progress = (processed_size * 100) / total_size
                                    speed = processed_size / (asyncio.get_event_loop().time() - start_time)
                                    await message.edit_text(
                                        f"Zipping: {progress:.1f}%\n"
                                        f"Speed: {format_size(speed)}/s"
                                    )
                                    
                            # Write file to zip
                            zf.write(
                                file_path,
                                arcname=Path(file_path).name
                            )
                            
                            # Clear memory after each file
                            await self._clear_memory()
                            
            zip_files.append(output_path)
            return zip_files
            
        except Exception as e:
            LOGGER.error(f"ZIP creation failed: {str(e)}")
            # Cleanup temp files
            for zip_file in zip_files:
                try:
                    if Path(zip_file).exists():
                        Path(zip_file).unlink()
                except:
                    pass
            raise e
