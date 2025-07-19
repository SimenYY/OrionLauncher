from Utils.abc import Repository
from Utils.path import base_path, exe_path, cwd_path, data_path


class Path(Repository):
    def __init__(self):
        super().__init__()

path = Path()
path.update({
    "base_path": base_path,
    "exe_path": exe_path,
    "cwd_path": cwd_path,
    "data_path": data_path
})
