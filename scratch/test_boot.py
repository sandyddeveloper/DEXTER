import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import boot_sequence

async def test_boot():
    print("Starting Terminal UI Boot Sequence Test...")
    await boot_sequence()
    print("Boot sequence complete.")

if __name__ == "__main__":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    asyncio.run(test_boot())
