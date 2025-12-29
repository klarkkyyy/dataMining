#!/usr/bin/env python3
"""
Script to correct social_platform_preference in the dataset based on realistic age demographics.
Reads social_media_vs_productivity_fixed.csv and creates social_media_vs_productivity_CORRECTED.csv
"""

import csv
import random

# Set random seed for reproducibility
random.seed(42)

# Define age-based platform probabilities
AGE_PLATFORM_PROBABILITIES = {
    'teen': {  # 18-19
        'platforms': ['TikTok', 'Instagram', 'Twitter', 'Facebook'],
        'probabilities': [0.45, 0.35, 0.15, 0.05]
    },
    'young_adult': {  # 20-29
        'platforms': ['Instagram', 'TikTok', 'Twitter', 'Facebook'],
        'probabilities': [0.40, 0.30, 0.20, 0.10]
    },
    'adult': {  # 30-39
        'platforms': ['Facebook', 'Instagram', 'Twitter', 'Telegram'],
        'probabilities': [0.35, 0.30, 0.20, 0.15]
    },
    'middle_aged': {  # 40-49
        'platforms': ['Facebook', 'Instagram', 'Twitter', 'Telegram'],
        'probabilities': [0.50, 0.25, 0.15, 0.10]
    },
    'mature_adult': {  # 50-59
        'platforms': ['Facebook', 'Instagram', 'Twitter', 'Telegram'],
        'probabilities': [0.60, 0.20, 0.15, 0.05]
    },
    'senior': {  # 60+
        'platforms': ['Facebook', 'Instagram', 'Twitter', 'Telegram'],
        'probabilities': [0.70, 0.15, 0.10, 0.05]
    }
}


def get_age_group(age):
    """
    Classify age into age groups.
    
    Args:
        age: Age as a float or None
        
    Returns:
        Age group key string or None
    """
    if age is None or age == '':
        return None
    
    age = float(age)
    
    if 18 <= age < 20:
        return 'teen'
    elif 20 <= age < 30:
        return 'young_adult'
    elif 30 <= age < 40:
        return 'adult'
    elif 40 <= age < 50:
        return 'middle_aged'
    elif 50 <= age < 60:
        return 'mature_adult'
    elif age >= 60:
        return 'senior'
    else:
        return None


def assign_platform_by_age(age):
    """
    Assign a social media platform based on age group probabilities.
    
    Args:
        age: Age as a float or string or None
        
    Returns:
        Platform name or empty string if age is missing
    """
    if age is None or age == '':
        return ''
    
    age_group = get_age_group(age)
    
    if age_group is None:
        return ''
    
    platforms = AGE_PLATFORM_PROBABILITIES[age_group]['platforms']
    probabilities = AGE_PLATFORM_PROBABILITIES[age_group]['probabilities']
    
    # Use random.choices for weighted random selection
    selected_platform = random.choices(platforms, weights=probabilities, k=1)[0]
    
    return selected_platform


def correct_csv_platforms(input_file, output_file):
    """
    Read CSV, correct social_platform_preference column, and write to new CSV.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    """
    rows_processed = 0
    rows_corrected = 0
    
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Process each row
        for row in reader:
            rows_processed += 1
            
            # Get age and assign new platform
            age = row.get('age', '')
            if age:
                new_platform = assign_platform_by_age(age)
                row['social_platform_preference'] = new_platform
                rows_corrected += 1
            # If age is missing, keep the original platform (or empty)
            
            writer.writerow(row)
    
    print(f"Processing complete!")
    print(f"  Total rows processed: {rows_processed}")
    print(f"  Rows with corrected platforms: {rows_corrected}")
    print(f"  Output file: {output_file}")


def verify_distribution(csv_file):
    """
    Verify the platform distribution by age group in the corrected file.
    
    Args:
        csv_file: Path to CSV file to analyze
    """
    from collections import defaultdict, Counter
    
    age_group_platforms = defaultdict(list)
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            age = row.get('age', '')
            platform = row.get('social_platform_preference', '')
            
            if age and platform:
                age_group = get_age_group(age)
                if age_group:
                    age_group_platforms[age_group].append(platform)
    
    print("\nPlatform distribution by age group:")
    print("=" * 70)
    
    age_group_names = {
        'teen': 'Teen (18-19)',
        'young_adult': 'Young Adult (20-29)',
        'adult': 'Adult (30-39)',
        'middle_aged': 'Middle-Aged (40-49)',
        'mature_adult': 'Mature Adult (50-59)',
        'senior': 'Senior (60+)'
    }
    
    for group in ['teen', 'young_adult', 'adult', 'middle_aged', 'mature_adult', 'senior']:
        if group in age_group_platforms:
            platforms = age_group_platforms[group]
            total = len(platforms)
            counter = Counter(platforms)
            
            print(f"\n{age_group_names[group]} (n={total}):")
            for platform, count in counter.most_common():
                percentage = (count / total) * 100
                print(f"  {platform:12s}: {count:6d} ({percentage:5.2f}%)")


if __name__ == '__main__':
    input_file = 'social_media_vs_productivity_fixed.csv'
    output_file = 'social_media_vs_productivity_CORRECTED.csv'
    
    print("Correcting social media platform preferences based on age demographics...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    correct_csv_platforms(input_file, output_file)
    
    print("\n" + "=" * 70)
    verify_distribution(output_file)
