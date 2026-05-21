import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Load the dataset containing historical study records
df = pd.read_csv('study_management.csv')

# --- DATA ANALYSIS LOGIC ---
# Efficiency is calculated by comparing actual time spent to estimated time.
# A score of 1.0 means the estimate was perfect. 
# Scores higher than 1.0 indicate that the actual time spent exceeded the estimate.
df['Efficiency'] = df['Actual_Hours_Spent'] / df['Estimated_Hours']

# Aggregate stats to find averages for each subject
stats = df.groupby('Subject').agg({
    'Efficiency': 'mean',
    'Completion_Status': 'mean',
    'Difficulty_Level': 'mean'
}).reset_index()

# Identification of performance categories
# Most Productive Subject: High completion rate even with higher difficulty levels
most_productive = stats.sort_values(by=['Completion_Status', 'Difficulty_Level'], ascending=False).iloc[0]

# Subject with Highest Time Variance: Highest efficiency score (takes longer than planned)
time_waster = stats.sort_values(by='Efficiency', ascending=False).iloc[0]

# --- PREDICTIVE MODELING ---
# We use a Random Forest Classifier to predict completion status based on task parameters
X = df[['Priority', 'Estimated_Hours', 'Difficulty_Level']]
# The label is what we are trying to predict (whether a task will be completed)
y = df['Label'] if 'Label' in df.columns else df['Completion_Status']

# Initialize and train the machine learning model
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

def show_results():
    """Prints the analysis report to the console."""
    print("=" * 40)
    print("      STUDY PERFORMANCE ANALYSIS REPORT")
    print("=" * 40)
    print(f"MOST PRODUCTIVE SUBJECT: {most_productive['Subject']}")
    print(f"Description: High completion rate maintained even for challenging tasks.")
    
    print(f"\nHIGHEST TIME VARIANCE SUBJECT: {time_waster['Subject']}")
    efficiency_percentage = round((time_waster['Efficiency'] - 1) * 100, 1)
    print(f"Observation: Session duration is typically {efficiency_percentage}% longer than estimated.")
    print("=" * 40)

if __name__ == "__main__":
    show_results()