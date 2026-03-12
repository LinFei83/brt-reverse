"""应用启动入口"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    from backend.config import HOST, PORT
    
    uvicorn.run(
        "backend.app:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
