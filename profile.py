import sys

if len(sys.argv) != 4:
    print("Usage: python profile.py <name> <age> <country>")
    sys.exit(1)

name = sys.argv[1]
age = sys.argv[2]
country = sys.argv[3]

print("=" * 30)
print("        PROFILE")
print("=" * 30)
print(f"Name    : {name}")
print(f"Age     : {age}")
print(f"Country : {country}")
print("=" * 30)
