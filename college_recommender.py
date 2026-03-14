import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from student_profile import StudentProfile

class CollegeRecommender:

    def __init__(self, data_file: str):

        self.colleges_df = pd.read_csv(data_file)
        
        self.weights = {
            'gpa': 0.35,        
            'budget': 0.30,      
            'program': 0.25,     
            'scholarship': 0.10  
        }
        
        assert abs(sum(self.weights.values()) - 1.0) < 0.01, "Weights must sum to 1.0"
        
        print(f"Loaded {len(self.colleges_df)} colleges successfully!")
    
    def calculate_gpa_score(self, student_gpa: float, college_gpa_req: float) -> float:
        if student_gpa >= college_gpa_req:
            extra = min((student_gpa - college_gpa_req) / 0.5, 0.2)
            return min(1.0 + extra, 1.2)
        else:
            deficit = (college_gpa_req - student_gpa) / college_gpa_req
            return max(0, 1.0 - deficit * 2) 
    
    def calculate_budget_score(self, student_budget: float, college_fees: float) -> float:
        if student_budget >= college_fees:
            savings = (student_budget - college_fees) / student_budget
            return 1.0 + min(savings, 0.2)  
        else:
            over_by = (college_fees - student_budget) / student_budget
            if over_by <= 0.2:  
                return 0.8 - over_by
            else:
                return max(0, 0.6 - over_by * 0.5) 
    
    def calculate_program_score(self, student_program: str, college_program: str) -> float:
        student_program = student_program.lower().strip()
        college_program = college_program.lower().strip()
        
        if student_program == college_program:
            return 1.0
        
        related_fields = {
            'computer science': ['cs', 'computing', 'software', 'it', 'information technology'],
            'engineering': ['engineer', 'mechanical', 'electrical', 'civil', 'chemical'],
            'business': ['management', 'finance', 'marketing', 'accounting', 'economics'],
            'humanities': ['arts', 'history', 'philosophy', 'literature', 'language'],
            'science': ['biology', 'chemistry', 'physics', 'mathematics', 'stats']
        }
        
        for field, related in related_fields.items():
            if (student_program in field or field in student_program or
                student_program in related or college_program in related):
                return 0.5
        
        return 0.0
    
    def calculate_scholarship_score(self, wants_scholarship: bool, has_scholarship: str) -> float:
        if not wants_scholarship:
            return 1.0 
        
        # Check if college offers scholarships
        if pd.notna(has_scholarship) and has_scholarship.lower() != 'no' and has_scholarship.lower() != 'none':
            if 'merit' in has_scholarship.lower():
                return 1.2 
            return 1.0  # Scholarship available
        else:
            return 0.0  # No scholarship available
    
    def calculate_compatibility_score(self, student: StudentProfile, college: Dict) -> float:

        gpa_score = self.calculate_gpa_score(student.gpa, college['gpa_requirement'])
        budget_score = self.calculate_budget_score(student.budget, college['fees'])
        program_score = self.calculate_program_score(student.preferred_program, college['program'])
        scholarship_score = self.calculate_scholarship_score(student.wants_scholarship, college['scholarship'])
        
        # Weighted sum
        total_score = (
            self.weights['gpa'] * gpa_score +
            self.weights['budget'] * budget_score +
            self.weights['program'] * program_score +
            self.weights['scholarship'] * scholarship_score
        )
        
        # Bonus for top-ranked colleges
        if 'ranking' in college:
            ranking_bonus = max(0, 1.0 - (college['ranking'] / 100)) * 0.1
            total_score += ranking_bonus
        
        return total_score
    
    def get_recommendations(self, student: StudentProfile, top_n: int = 10) -> pd.DataFrame:

        scores = []
        for _, college in self.colleges_df.iterrows():
            score = self.calculate_compatibility_score(student, college.to_dict())
            scores.append(score)
        
        self.colleges_df['compatibility_score'] = scores

        recommendations = self.colleges_df.nlargest(top_n, 'compatibility_score')
        
        recommendations['compatibility_percentage'] = (recommendations['compatibility_score'] * 100).round(1)
        
        return recommendations
    
    def explain_recommendation(self, student: StudentProfile, college_name: str) -> Dict:

        college = self.colleges_df[self.colleges_df['college_name'] == college_name].iloc[0]
        
        return {
            'college': college_name,
            'scores': {
                'gpa': self.calculate_gpa_score(student.gpa, college['gpa_requirement']),
                'budget': self.calculate_budget_score(student.budget, college['fees']),
                'program': self.calculate_program_score(student.preferred_program, college['program']),
                'scholarship': self.calculate_scholarship_score(student.wants_scholarship, college['scholarship'])
            },
            'details': {
                'gpa_required': college['gpa_requirement'],
                'fees': college['fees'],
                'program': college['program'],
                'scholarship': college['scholarship']
            }
        }
    
    def filter_by_field(self, field: str) -> pd.DataFrame:
        field_keywords = {
            'STEM': ['computer science', 'engineering', 'mathematics', 'science', 'cs', 'math', 'physics', 'chemistry', 'biology'],
            'Management': ['business', 'management', 'finance', 'marketing', 'accounting', 'economics'],
            'Humanities': ['humanities', 'arts', 'history', 'philosophy', 'literature', 'language']
        }
        
        if field in field_keywords:
            keywords = field_keywords[field]
            mask = self.colleges_df['program'].str.lower().apply(
                lambda x: any(kw in x for kw in keywords)
            )
            return self.colleges_df[mask]
        else:
            return self.colleges_df