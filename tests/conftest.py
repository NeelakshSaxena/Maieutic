import atexit
import os
import shutil
import tempfile

# Point the app at a throwaway SQLite file before any `app.*` module is imported, so test runs
# never create tables in (or otherwise modify) the tracked maieutic.db files.
_tmp_dir = tempfile.mkdtemp(prefix="mentorai-tests-")
atexit.register(shutil.rmtree, _tmp_dir, ignore_errors=True)  # best effort: Windows may still hold the file
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_tmp_dir, "test.db").replace(os.sep, "/")
