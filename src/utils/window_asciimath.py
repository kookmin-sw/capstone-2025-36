import site
import os
from utils.logger import init_logger

logger = init_logger(__file__, "DEBUG")

def modify_init_py():
    """
    윈도우 환경에서 py_asciimath를 사용하기 위해서
    설치된 site-packages 디렉토리 목록에서  __init__.py를 변경하는 함수
    
    """
    site_packages_dirs = site.getsitepackages()
    
    for site_dir in site_packages_dirs:
        asciimath_dir = os.path.join(site_dir, "py_asciimath")
        init_file = os.path.join(asciimath_dir, "__init__.py")
        
        if os.path.exists(init_file):
            new_content = (
                "import platform\n"
                "import os\n\n"
                "if (platform.system() == 'Windows'):\n"
                "    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__)).replace('\\\\', '/')\n"
                "else:\n"
                "    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))\n"
                "__version__ = \"0.3.0\"\n"

            )
            
            with open(init_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            logger.info(f"Updated py-asciimath: {init_file}")
            return
        
    logger.error("py-asciimath module not found.")