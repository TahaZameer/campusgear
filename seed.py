from datetime import date
from dotenv import load_dotenv
load_dotenv()

from app.database import LocalSession
from app.models import User, Category, Item
from app.enums import Role, ItemCondition, ItemStatus
from app.auth import password_hashing

def seed():
    db = LocalSession()

    try:
        # Users
        admin = User(
            full_name="Seed Admin",
            email="admin@campusgear.com",
            password_hash=password_hashing.hash("admin123"),
            role=Role.admin,
        )

        staff = User(
            full_name="Seed Staff",
            email="staff@campusgear.com",
            password_hash=password_hashing.hash("staff123"),
            role=Role.staff,
        )

        member = User(
            full_name="Seed Member",
            email="member@campusgear.com",
            password_hash=password_hashing.hash("member123"),
            role=Role.member,
        )

        # Categories
        cameras = Category(
            name="Cameras",
            description="Camera equipment"
        )

        laptops = Category(
            name="Laptops",
            description="Laptop equipment"
        )

        db.add_all([admin, staff, member, cameras, laptops])
        db.flush()

        # Items
        camera = Item(
            name="Canon EOS R50",
            category_id=cameras.id,
            asset_code="CAM-001",
            description="Mirrorless camera",
            condition=ItemCondition.good,
            purchase_date=date(2025, 1, 10),
            status=ItemStatus.available,
        )

        laptop = Item(
            name="Dell Latitude",
            category_id=laptops.id,
            asset_code="LAP-001",
            description="Student laptop",
            condition=ItemCondition.excellent,
            purchase_date=date(2025, 2, 15),
            status=ItemStatus.available,
        )

        db.add_all([camera, laptop])

        db.commit()

        print("Seed data created successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()