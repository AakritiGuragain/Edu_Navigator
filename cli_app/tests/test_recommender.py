import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from college_recommender import CollegeRecommender
from student_profile import StudentProfile

def test_recommender():
    recommender = CollegeRecommender('data/mock_colleges.csv')
    
    test_students = [
        StudentProfile(50000, 3.9, "Computer Science", True),
        StudentProfile(30000, 3.2, "Engineering", False),
        StudentProfile(25000, 2.5, "Business", True),
    ]
    
    for i, student in enumerate(test_students, 1):
        print(f"\nTest Student {i}:")
        print(student)
        recommendations = recommender.get_recommendations(student, top_n=5)
        print("\nTop Recommendations:")
        print(recommendations[['college_name', 'compatibility_percentage', 'program', 'fees']])

if __name__ == "__main__":
    test_recommender()