from werkzeug.security import generate_password_hash, check_password_hash
pw_hash = generate_password_hash('dog')
print(pw_hash)

print(check_password_hash(pw_hash,'dog'))
print(check_password_hash(pw_hash,'绕为王'))
