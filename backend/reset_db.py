from backend import habits  # adjust import according to your app structure

# Drop all tables
habits.drop_all()

# Recreate all tables according to your models
habits.create_all()

print("Database cleared and tables recreated!")
