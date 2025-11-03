# ForBRO

Notes:

Todo:

        1. Do a Salary History stores in firestore
        2. Maybe add screenshots for important excel format example
        3. Maybe after running everything, give a summary of what's going on(or error summary)?

        4. when deploy, delete from initialize_firestore() from utils.py
                "# 2. Try local credential file (for development)
                if cred is None:
                     local_cred_path = "Credential/bro-salary-firebase-adminsdk-fbsvc-cf452594f8.json""
        5. when deploy, change "password_hash" in firestore_auth.py to secret key "password_hash": hash_password("admin123"),  # Change this password!
