# myapp/storage.py

from whitenoise.storage import CompressedManifestStaticFilesStorage

class CustomStaticFilesStorage(CompressedManifestStaticFilesStorage):
    def _save(self, name, content):
        try:
            return super()._save(name, content)
        except OSError:
            # Log the error and continue without raising an exception
            self.logger.warning(f"Skipping missing file: {name}")
            return None
