class AdviceUnavailable(RuntimeError):
    """Le conseil n'a pas pu être produit : rien n'est enregistré, rien n'est montré."""


class DiagnosticNotRecorded(RuntimeError):
    """Le diagnostic n'a pas pu être enregistré : il n'est donc pas montré."""
