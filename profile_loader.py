from importlib.machinery import ModuleSpec
import importlib.util

def load_profile(profile_path: str) -> type:
    """動態加載 Profile 類"""
    try:
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