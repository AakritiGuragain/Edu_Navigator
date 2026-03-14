import os
from college_recommender import CollegeRecommender
from student_profile import StudentProfile

def display_welcome():
    print("=" * 60)
    print("     EDUCATION NAVIGATOR - College Recommendation System")
    print("=" * 60)
    print("\nFind the perfect college based on your academic profile!")
    print("-" * 60)

def get_student_input() -> StudentProfile:
    print("\n Please enter your details:")
    print("-" * 40)
    
    while True:
        try:
            budget = float(input("Your budget for tuition ($/year): $"))
            if budget > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            gpa = float(input("Your GPA (on 4.0 scale): "))
            if 0 <= gpa <= 4.0:
                break
            print("GPA must be between 0 and 4.0.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\nAvailable fields: Computer Science, Engineering, Business, Humanities, etc.")
    program = input("Preferred program: ").strip()
    
    while True:
        scholarship_input = input("Do you need scholarship? (yes/no): ").lower().strip()
        if scholarship_input in ['yes', 'y', 'no', 'n']:
            wants_scholarship = scholarship_input in ['yes', 'y']
            break
        print("Please enter 'yes' or 'no'.")
    
    return StudentProfile(budget, gpa, program, wants_scholarship)

def display_recommendations(recommendations, student):
    """Display recommendations in a formatted way"""
    print("\n" + "=" * 70)
    print("🎓 YOUR TOP COLLEGE RECOMMENDATIONS")
    print("=" * 70)
    
    if recommendations.empty:
        print("\nNo colleges found matching your criteria.")
        return
    
    for idx, (_, college) in enumerate(recommendations.iterrows(), 1):
        print(f"\n{idx}.   {college['college_name']} ({college['city']}, {college['state']})")
        print(f"   └─ Match: {college['compatibility_percentage']}%")
        print(f"   └─ Program: {college['program']}")
        print(f"   └─ Tuition: ${college['fees']:,}/year")
        print(f"   └─ GPA Required: {college['gpa_requirement']}")
        print(f"   └─ Scholarship: {college['scholarship']}")
        print(f"   └─ Ranking: #{college['ranking']}")

def main():
    display_welcome()
    
    data_file = 'data/mock_colleges.csv'
    if not os.path.exists(data_file):
        print(f"\n Error: Data file '{data_file}' not found!")
        print("Please make sure the file exists in the data folder.")
        return
    
    try:
        print("\n Loading college database...")
        recommender = CollegeRecommender(data_file)
        
        # Get student profile
        student = get_student_input()
        
        print("\n" + "=" * 60)
        print("YOUR PROFILE SUMMARY")
        print("=" * 60)
        print(student)
        
        print("\n Analyzing colleges...")
        recommendations = recommender.get_recommendations(student, top_n=10)
        
        display_recommendations(recommendations, student)
        
        print("\n" + "-" * 60)
        if len(recommendations) > 0:
            explain = input("\nWould you like detailed explanation for a specific college? (yes/no): ").lower()
            if explain in ['yes', 'y']:
                college_name = input("Enter college name: ").strip()
                try:
                    explanation = recommender.explain_recommendation(student, college_name)
                    print("\nDETAILED ANALYSIS")
                    print("-" * 40)
                    print(f"College: {explanation['college']}")
                    print("\nScore Breakdown:")
                    for factor, score in explanation['scores'].items():
                        percentage = score * 100
                        bar = "█" * int(percentage / 10)
                        print(f"  {factor.capitalize()}: {percentage:.1f}% {bar}")
                    print("\nCollege Details:")
                    for detail, value in explanation['details'].items():
                        print(f"  {detail.capitalize()}: {value}")
                except IndexError:
                    print(f"College '{college_name}' not found in database.")
        
        print("\n" + "=" * 60)
        print("Thank you for using Education Navigator!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n An error occurred: {e}")
        print("Please check your data file and try again.")

if __name__ == "__main__":
    main()