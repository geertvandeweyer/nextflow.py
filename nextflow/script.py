class Script:
    """A .nf file somewhere on the local filesystem."""

    def __init__(self, path):
        self.path = path
    

    def __repr__(self):
        return f"<Script ({self.path})>"