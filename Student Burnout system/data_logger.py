import pandas as pd
import os

def manage_data():
    """Manages the logging of student daily activity data into a CSV file."""
    file_name = 'student_pulse.csv'
    
    # Check if the data file exists. If not, create it with some sample records.
    if not os.path.isfile(file_name):
        print(f"Creating {file_name} with initial sample data...")
        
        # initial_data dictionary holds sample records for Sleep, Study, ScreenTime, and Mood
        initial_data = {
            'Date': [f'{i:02d}-05-2026' for i in range(1, 21)],
            'Sleep': [8.0, 7.5, 4.0, 5.0, 8.5, 7.0, 4.5, 9.0, 6.0, 3.5, 7.0, 5.5, 8.0, 4.0, 7.5, 8.2, 4.2, 5.5, 7.8, 4.0],
            'Study': [4.0, 5.0, 9.0, 8.0, 3.0, 6.0, 7.5, 2.0, 5.0, 10.0, 4.0, 8.5, 5.0, 6.0, 5.5, 3.5, 9.5, 8.0, 4.5, 7.0],
            'ScreenTime': [2.0, 1.5, 3.0, 4.0, 1.0, 2.0, 5.0, 1.0, 3.5, 2.0, 4.0, 3.0, 1.0, 6.0, 2.5, 1.2, 3.5, 4.5, 2.0, 5.5],
            'Mood': [8, 7, 3, 4, 9, 6, 2, 10, 5, 2, 6, 3, 8, 3, 7, 9, 2, 4, 8, 3],
            'Label': [0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1]
        }
        
        # Convert dictionary to a pandas DataFrame and save to CSV
        df = pd.DataFrame(initial_data)
        df.to_csv(file_name, index=False)
        print("Data initialization complete. You can now use predictor.py for analysis.")
    else:
        # If file exists, allow the user to manually enter today's data
        print("--- Daily Data Logging ---")
        date = input("Enter Date (DD-MM-YYYY): ")
        sleep = float(input("Hours of Sleep: "))
        study = float(input("Hours of Study: "))
        screen = float(input("Screen Time (hours): "))
        mood = int(input("Mood Level (1-10): "))
        
        # Basic logic to determine if the student is likely 'Burnt Out' (Label 1)
        # burnout = high study hours, low sleep, or low mood
        label = 1 if (study > 6 and sleep < 5) or mood < 4 else 0
        
        # Create a new DataFrame for the single row of data
        new_row = pd.DataFrame([[date, sleep, study, screen, mood, label]], 
                               columns=['Date', 'Sleep', 'Study', 'ScreenTime', 'Mood', 'Label'])
        
        # Append the new row to the existing CSV file without writing the header again
        new_row.to_csv(file_name, mode='a', header=False, index=False)
        print("Entry has been successfully saved to student_pulse.csv.")

if __name__ == "__main__":
    manage_data()