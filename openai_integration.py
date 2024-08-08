# import subprocess
#
#
# def check_comment(comment: str) -> bool:
#     result = subprocess.run(
#         ['python', 'profanity_checker.py', comment],
#         capture_output=True,
#         text=True
#     )
#     return result.stdout.strip().lower() == 'true'
