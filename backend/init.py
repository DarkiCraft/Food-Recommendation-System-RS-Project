import os
from dotenv import load_dotenv
load_dotenv()

import random
from datetime import datetime, timedelta
import bcrypt

from database import engine, session_local
from models.base import Base
from models.user import UserModel
from models.item import ItemModel
from models.interaction import InteractionModel, InteractionType
from models.order import OrderModel
from models.rating import RatingModel
from repos.interaction import InteractionRepo
from repos.item import ItemRepo
from repos.user import UserRepo
from services.recommend import RecommendationService

# Constants
NUM_USERS = 50
NUM_ITEMS = 200
NUM_INTERACTIONS = 3000

CUISINES = [
    "Japanese", "Italian", "Mexican", "Indian", "Fast Food", 
    "Chinese", "Thai", "French", "Mediterranean", "Korean", 
    "American", "Middle Eastern", "Vietnamese"
]

FOOD_NOUNS = {
    "Japanese": ["Sushi", "Ramen", "Udon", "Tempura", "Sashimi", "Mochi", "Bento", "Onigiri", "Takoyaki", "Yakitori", "Tonkatsu", "Soba"],
    "Italian": ["Pizza", "Pasta", "Lasagna", "Risotto", "Gelato", "Tiramisu", "Bruschetta", "Ravioli", "Gnocchi", "Cannoli", "Focaccia", "Calzone"],
    "Mexican": ["Taco", "Burrito", "Enchilada", "Quesadilla", "Churro", "Guacamole", "Fajita", "Tamale", "Tostada", "Carnitas", "Ceviche"],
    "Indian": ["Curry", "Naan", "Samosa", "Biryani", "Dosa", "Tandoori", "Paneer", "Chutney", "Tikka Masala", "Vindaloo", "Pakora"],
    "Fast Food": ["Burger", "Fries", "Nuggets", "Hot Dog", "Milkshake", "Onion Rings", "Wrap", "Chicken Sandwich", "Tater Tots", "Sundae"],
    "Chinese": ["Dim Sum", "Fried Rice", "Chow Mein", "Peking Duck", "Spring Roll", "Baozi", "Wonton", "Mapo Tofu", "Kung Pao Chicken"],
    "Thai": ["Pad Thai", "Tom Yum", "Green Curry", "Red Curry", "Som Tum", "Mango Sticky Rice", "Satay", "Massaman Curry"],
    "French": ["Croissant", "Baguette", "Crepe", "Escargot", "Macaron", "Ratatouille", "Quiche", "Coq au Vin", "Souffle"],
    "Mediterranean": ["Falafel", "Hummus", "Gyro", "Pita", "Shawarma", "Baklava", "Tzatziki", "Moussaka", "Baba Ganoush"],
    "Korean": ["Bibimbap", "Kimchi", "Bulgogi", "Tteokbokki", "Kimbap", "Japchae", "Samgyeopsal", "Bingsu", "Galbi"],
    "American": ["BBQ Ribs", "Steak", "Mac and Cheese", "Apple Pie", "Pancakes", "Waffles", "Cornbread", "Buffalo Wings", "Cheesecake"],
    "Middle Eastern": ["Kebab", "Tabouleh", "Shakshuka", "Kofta", "Fattoush", "Mansaf", "Halva", "Manakish"],
    "Vietnamese": ["Pho", "Banh Mi", "Spring Rolls", "Bun Cha", "Banh Xeo", "Che", "Ca Phe Sua Da", "Goi Cuon"]
}

ADJECTIVES = [
    "Spicy", "Sweet", "Savory", "Classic", "Deluxe", "Premium", "Crispy", "Cheesy", "Zesty",
    "Smoky", "Tangy", "Rich", "Creamy", "Crunchy", "Buttery", "Garlicky", "Herb-crusted",
    "Roasted", "Grilled", "Fried", "Baked", "Steamed", "Fresh", "Hearty", "Light",
    "Gourmet", "Authentic", "Traditional", "Modern", "Fusion", "Signature", "Ultimate",
    "Secret-Recipe", "Handcrafted", "Artisan", "Rustic", "Homestyle", "Chunky", "Smooth"
]

def generate_items(db):
    print("Generating items...")
    items = []
    for i in range(NUM_ITEMS):
        cuisine = random.choice(CUISINES)
        noun = random.choice(FOOD_NOUNS[cuisine])
        adj = random.choice(ADJECTIVES)
        item_name = f"{adj} {noun} {i}"
        
        item = ItemModel(item_name=item_name, cuisine=cuisine)
        db.add(item)
        items.append(item)
    
    db.commit()
    for item in items: db.refresh(item)
    return items

def generate_users(db):
    print("Generating users...")
    users = []
    # Severe obfuscation: generic names, generic emails, same hash
    mock_hash = bcrypt.hashpw(b"mockpassword", bcrypt.gensalt())
    
    for i in range(NUM_USERS):
        user = UserModel(
            user_name=f"mock_user_{i}",
            email=f"mock_user_{i}@fake.local",
            password_hash=mock_hash,
            signup_date=datetime.now() - timedelta(days=random.randint(30, 365))
        )
        db.add(user)
        users.append(user)
        
    db.commit()
    for user in users: db.refresh(user)
    return users

def generate_interactions(db, users, items):
    print("Generating interactions...")
    user_favorites = {user.user_id: random.choice(CUISINES) for user in users}
    
    items_by_cuisine = {cuisine: [] for cuisine in CUISINES}
    for item in items:
        items_by_cuisine[item.cuisine].append(item)

    now = datetime.now()
    interactions_count = 0
    orders_count = 0
    ratings_count = 0

    for _ in range(NUM_INTERACTIONS):
        user = random.choice(users)
        fav_cuisine = user_favorites[user.user_id]
        
        if random.random() < 0.85:
            item = random.choice(items_by_cuisine[fav_cuisine])
        else:
            item = random.choice(items)
            
        interaction_type = InteractionType.CLICK
        is_order = random.random() < 0.3
        if is_order:
            interaction_type = InteractionType.ORDER
            
        ts = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 24))
        
        interaction = InteractionModel(
            user_id=user.user_id,
            item_id=item.item_id,
            interaction_type=interaction_type,
            timestamp=ts
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        interactions_count += 1
        
        if is_order:
            order = OrderModel(
                user_id=user.user_id,
                item_id=item.item_id,
                timestamp=ts
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            orders_count += 1
            
            if random.random() < 0.8:
                if item.cuisine == fav_cuisine:
                    rating_val = random.randint(4, 5)
                else:
                    rating_val = random.randint(1, 5)
                    
                rating = RatingModel(
                    order_id=order.order_id,
                    timestamp=ts,
                    rating=rating_val
                )
                db.add(rating)
                db.commit()
                ratings_count += 1

    print(f"Generated {interactions_count} interactions, {orders_count} orders, {ratings_count} ratings.")

def main():
    print("NUKING DATABASE... Clearing all old data and resetting sequences.")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = session_local()
    
    artifact_path = os.path.join(os.path.dirname(__file__), "artifacts", "ncf_model.pth")
    if os.path.exists(artifact_path):
        print("Deleting old NCF model artifact...")
        os.remove(artifact_path)
    
    items = generate_items(db)
    users = generate_users(db)
    generate_interactions(db, users, items)
    
    print("Retraining Recommender System natively...")
    interaction_repo = InteractionRepo(db)
    item_repo = ItemRepo(db)
    user_repo = UserRepo(db)
    
    service = RecommendationService(interaction_repo, item_repo, user_repo)
    service.retrain()
    
    print("Bootstrapping complete! (Interactions left in DB because SVD/Popularity models require them to be loaded on API server start).")
    db.close()

if __name__ == "__main__":
    main()
