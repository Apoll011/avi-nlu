from fastapi import Request
from src.kit import IntentKit


def get_kit(request: Request) -> IntentKit:
    return request.app.state.intentKit
