import hashlib
class SignatureGenerator:
    def generate(self, normalized_tree):
        return hashlib.sha256(str(normalized_tree).encode()).hexdigest()
