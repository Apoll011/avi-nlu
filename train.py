import sys

from kit import IntentKit

print("Starting Training")
intentKit = IntentKit()
intentKit.train(sys.argv[1] if len(sys.argv) > 1 else "en")