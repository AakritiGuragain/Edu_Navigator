class CollegeRankingSystem:
    def __init__(self, weight_gpa=0.4, weight_budget=0.3, weight_program=0.2, weight_scholarship=0.1):
        """
        Initialize the ranking system with customizable weights.
        The weights should sum to 1.0 (or 100%).
        """
        self.weights = {
            'gpa': weight_gpa,
            'budget': weight_budget,
            'program': weight_program,
            'scholarship': weight_scholarship
        }

    def calculate_compatibility_score(self, student_profile, college):
        """
        Calculates a compatibility score for a single college based on the student's profile.
        Returns a score between 0 and 100.
        """
        score = 0
        max_possible_score = 100

        # 1. GPA Match (Weight: 40%)
        # If student GPA is greater than or equal to requirement, full points for this section.
        # If lower, deduct points based on how far off they are.
        if student_profile['gpa'] >= college['gpa_requirement']:
            gpa_score = 100
        else:
            # Example penalty: lose points proportionally to the gap
            gap = college['gpa_requirement'] - student_profile['gpa']
            gpa_score = max(0, 100 - (gap * 50))  # e.g., 0.5 gap = 25 points lost

        # 2. Budget vs Fees (Weight: 30%)
        # If fees are within budget, full points.
        # If fees exceed budget, decrease score.
        if college['fees'] <= student_profile['budget']:
            budget_score = 100
        else:
            excess = college['fees'] - student_profile['budget']
            budget_penalty = (excess / student_profile['budget']) * 100
            budget_score = max(0, 100 - budget_penalty)

        # 3. Program/Field Match (Weight: 20%)
        # Binary: 100 if the college offers the program, 0 if not.
        if student_profile['preferred_program'].lower() in [p.lower() for p in college['programs']]:
            program_score = 100
        else:
            program_score = 0  # Crucial factor, could also just filter these out entirely

        # 4. Scholarship Availability (Weight: 10%)
        # If student wants scholarship and college offers it, full points.
        scholarship_score = 0
        if student_profile['scholarship_interest']:
            if college['scholarship_available']:
                scholarship_score = 100
            else:
                scholarship_score = 0
        else:
            # If student doesn't care, give neutral/full points so they aren't penalized
            scholarship_score = 100

        # Calculate weighted total
        total_score = (
            (gpa_score * self.weights['gpa']) +
            (budget_score * self.weights['budget']) +
            (program_score * self.weights['program']) +
            (scholarship_score * self.weights['scholarship'])
        )

        return round(total_score, 2)

    def rank_colleges(self, student_profile, college_dataset):
        """
        Takes a student profile and a list of college dictionaries.
        Returns a sorted list of colleges with their compatibility scores.
        """
        ranked_list = []

        for college in college_dataset:
            score = self.calculate_compatibility_score(student_profile, college)
            
            # Optional: Filter out colleges that don't offer the preferred program at all
            if student_profile['preferred_program'].lower() not in [p.lower() for p in college['programs']]:
                continue # Skip this college entirely

            ranked_list.append({
                'college_name': college['college_name'],
                'compatibility_score': score,
                'details': college # Keep original data for UI display
            })

        # Sort the list by compatibility_score in descending order (highest first)
        ranked_list.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return ranked_list


# --- Example Usage ---
if __name__ == "__main__":
    # 1. Example Student Profile
    student = {
        'name': 'Alex',
        'gpa': 3.6,
        'budget': 20000,
        'preferred_program': 'Computer Science',
        'scholarship_interest': True
    }

    # 2. Example Database Results (Mock Data)
    colleges = [
        {
            'college_name': 'Tech University',
            'programs': ['Computer Science', 'Engineering', 'Mathematics'],
            'fees': 18000,
            'gpa_requirement': 3.5,
            'scholarship_available': True
        },
        {
            'college_name': 'State College',
            'programs': ['Business', 'Computer Science', 'Humanities'],
            'fees': 22000,
            'gpa_requirement': 3.2,
            'scholarship_available': False
        },
        {
            'college_name': 'Elite Institute',
            'programs': ['Computer Science', 'Data Science'],
            'fees': 35000,
            'gpa_requirement': 3.9,
            'scholarship_available': True
        },
        {
            'college_name': 'Arts Academy',
            'programs': ['Fine Arts', 'Design'],
            'fees': 15000,
            'gpa_requirement': 3.0,
            'scholarship_available': True
        }
    ]

    # 3. Run the algorithm
    ranking_system = CollegeRankingSystem()
    recommendations = ranking_system.rank_colleges(student, colleges)

    # 4. Output results
    print(f"Top College Recommendations for {student['name']}:\\n")
    for rank, rec in enumerate(recommendations, 1):
        print(f"{rank}. {rec['college_name']} - Match Score: {rec['compatibility_score']}/100")
        print(f"   Fees: ${rec['details']['fees']} | Required GPA: {rec['details']['gpa_requirement']}")
        print(f"   Scholarship: {'Yes' if rec['details']['scholarship_available'] else 'No'}")
        print("-" * 40)
