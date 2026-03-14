class StudentProfile:
    
    def __init__(self, budget, gpa, preferred_program, wants_scholarship=False):
    
        self.budget = float(budget)
        self.gpa = float(gpa)
        self.preferred_program = preferred_program
        self.wants_scholarship = wants_scholarship
    
    def __str__(self):
        scholarship_text = "Yes" if self.wants_scholarship else "No"
        return f"""
Student Profile:
- Budget: Rs.{self.budget:,}/year
- GPA: {self.gpa}
- Preferred Program: {self.preferred_program}
- Needs Scholarship: {scholarship_text}
        """
    
    def to_dict(self):
        """Convert profile to dictionary for storage"""
        return {
            'budget': self.budget,
            'gpa': self.gpa,
            'preferred_program': self.preferred_program,
            'wants_scholarship': self.wants_scholarship
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create profile from dictionary"""
        return cls(
            budget=data['budget'],
            gpa=data['gpa'],
            preferred_program=data['preferred_program'],
            wants_scholarship=data['wants_scholarship']
        )