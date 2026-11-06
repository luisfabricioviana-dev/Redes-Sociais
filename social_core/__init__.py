"""Editorial governance and learning contracts for Agente de Redes Sociais."""
from .engine import evaluate_candidate, record_learning, build_handoff, validate_final_package, LearningError
__all__ = ["evaluate_candidate", "record_learning", "build_handoff", "validate_final_package", "LearningError"]
