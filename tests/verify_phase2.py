import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, College, User, Review, ForumCategory, ForumPost, ForumComment

def verify_phase2():
    with app.app_context():
        # 1. Check Categories
        cats = ForumCategory.query.count()
        print(f"Forum Categories: {cats}")
        if cats < 4:
            print("FAILURE: Forum categories not seeded correctly.")
            return

        # 2. Get a user and a college
        user = User.query.first()
        college = College.query.first()
        if not user or not college:
            print("FAILURE: Nees a user and college for testing.")
            return

        # 3. Create a Review
        print(f"Testing Review for {college.name} by {user.username}...")
        review = Review(
            user_id=user.id,
            college_id=college.id,
            rating=5,
            comment="Excellent campus and faculty!"
        )
        db.session.add(review)
        db.session.commit()
        print("SUCCESS: Review created.")

        # 4. Create a Forum Post
        category = ForumCategory.query.first()
        print(f"Testing Forum Post in {category.name}...")
        post = ForumPost(
            user_id=user.id,
            category_id=category.id,
            title="How to prepare for IOE?",
            content="Any tips for the entrance exam?"
        )
        db.session.add(post)
        db.session.commit()
        print(f"SUCCESS: Post created with ID {post.id}.")

        # 5. Create a Comment
        print("Testing Forum Comment...")
        comment = ForumComment(
            user_id=user.id,
            post_id=post.id,
            content="Start with physics and math fundamentals."
        )
        db.session.add(comment)
        db.session.commit()
        print("SUCCESS: Comment created.")

        print("\nPhase 2 Verification PASSED!")

if __name__ == '__main__':
    verify_phase2()
