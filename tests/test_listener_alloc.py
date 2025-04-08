# from typing import Dict, List
# from backend.password import PasswordHash
# from backend.server import Listener, PermissionLevel, db
# from sqlalchemy.exc import IntegrityError, OperationalError
# from flask import jsonify
# import uuid
# import logging
#
# def createTestUser(
#     first_name: str,
#     last_name: str,
#     email: str,
#     password: str,
#     languages: List[Dict[str, str]]
# ):
#
#     user = Listener(
#         id = uuid.uuid4(),
#         first_name = first_name,
#         last_name = last_name,
#         email = email,
#         pw_hash = PasswordHash(password),
#         permission = PermissionLevel.listener,
#         background_info = "ahhhhhhhhhhhh",
#         reward_points = 0,
#         is_verified = True,
#         languages = languages,
#     )
#
#     try:
#         with db.session.begin_nested():
#             db.session.add(user)
#             db.session.commit()
#             # no need to send verification email for testing account
#     except IntegrityError as e:
#         db.session.rollback()
#         logging.debug(e)
#         return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
#     except Exception as e:
#         db.session.rollback()
#         logging.debug(e)
#         return jsonify({"error": "Error Code: 500"}), 500
#     return jsonify({"message": "Registration Successful"})
