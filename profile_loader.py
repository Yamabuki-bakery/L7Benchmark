from importlib.machinery import ModuleSpec
import importlib.util
import sys
import os


def is_frozen() -> bool:
    """更精准的打包环境判断"""
    return hasattr(sys, '_MEIPASS')


def load_profile(profile_path: str) -> type:
    try:
        profile_path = get_real_profile_path(profile_path)
        # 創建模塊規範
        spec: ModuleSpec | None = importlib.util.spec_from_file_location(
            "dynamic_profile", 
            profile_path
        )

        if spec is None:
            raise ImportError(f"Cannot load module from {profile_path}")
        
        # 創建並執行模塊
        module = importlib.util.module_from_spec(spec)
        
        if spec.loader is None:
            raise ImportError(f"Cannot load module from {profile_path}")
        spec.loader.exec_module(module)
        
        # 驗證接口合規性
        if not hasattr(module, 'ExportedProfile'):
            raise AttributeError("Profile must contain RequestGenerator class")
            
        return module.ExportedProfile
    except Exception as e:
        raise RuntimeError(f"Profile loading failed: {str(e)}")
    

def get_real_profile_path(profile_path: str) -> str:
    """优化后的路径解析逻辑"""
    search_paths: list[str] = []
    
    # 1. 绝对路径直接返回
    if os.path.isabs(profile_path):
        return profile_path
    
    # 2. 已存在的相对路径
    if os.path.exists(profile_path):
        return os.path.abspath(profile_path)
    
    # 3. 打包环境优先路径
    if is_frozen():
        # 3.1 PyInstaller 临时目录
        meipass_dir = getattr(sys, "_MEIPASS", "")
        search_paths.append(os.path.join(meipass_dir, 'profiles', f"{profile_path}.py"))
        # 3.2 可执行文件同级目录
        search_paths.append(os.path.join(os.path.dirname(sys.executable), 'profiles', f"{profile_path}.py"))
    
    # 4. 开发环境路径
    search_paths.extend([
        os.path.join(os.getcwd(), 'profiles', f"{profile_path}.py"),
        os.path.join(os.getcwd(), f"{profile_path}.py")
    ])
    
    # 5. 遍历所有候选路径
    for path in search_paths:
        if os.path.isfile(path):
            return path
    
    raise FileNotFoundError(f"Profile {profile_path} not found in:\n" + "\n".join(search_paths))