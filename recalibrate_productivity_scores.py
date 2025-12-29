#!/usr/bin/env python3
"""
Script to recalibrate productivity scores based on psychological research.
Adjusts perceived_productivity_score to match research-based perception gaps by age group.
"""

import csv
import random
from collections import defaultdict

# Set random seed for reproducibility
random.seed(42)

# Define age group mappings and expected gaps (Perceived - Actual)
AGE_GROUP_GAPS = {
    'teen': {  # 18-19
        'range': [18, 19],
        'gap_min': 1.5,
        'gap_max': 2.5,
        'description': 'Teens (18-19)'
    },
    'young_adult': {  # 20-29
        'range': [20, 29],
        'gap_min': 0.5,
        'gap_max': 1.5,
        'description': 'Young Adults (20-29)'
    },
    'adult': {  # 30-39
        'range': [30, 39],
        'gap_min': 0.0,
        'gap_max': 0.5,
        'description': 'Adults (30-39)'
    },
    'middle_aged': {  # 40-55
        'range': [40, 55],
        'gap_min': 0.0,
        'gap_max': 0.8,
        'description': 'Middle-Aged (40-55)'
    },
    'senior': {  # 56-65
        'range': [56, 65],
        'gap_min': -0.5,
        'gap_max': 1.0,
        'description': 'Seniors (56-65)'
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
    
    for group_key, group_info in AGE_GROUP_GAPS.items():
        min_age, max_age = group_info['range']
        if min_age <= age <= max_age:
            return group_key
    
    return None


def calculate_age_group_means(csv_file):
    """
    Calculate mean actual_productivity_score for each age group.
    Used for imputing missing actual productivity scores.
    
    Args:
        csv_file: Path to CSV file
        
    Returns:
        Dictionary mapping age group to mean actual productivity score
    """
    age_group_scores = defaultdict(list)
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            age = row.get('age', '')
            actual = row.get('actual_productivity_score', '')
            
            if age and actual:
                age_group = get_age_group(age)
                if age_group:
                    age_group_scores[age_group].append(float(actual))
    
    # Calculate means
    age_group_means = {}
    for group, scores in age_group_scores.items():
        if scores:
            age_group_means[group] = sum(scores) / len(scores)
    
    return age_group_means


def recalibrate_productivity_scores(input_file, output_file):
    """
    Recalibrate productivity scores based on psychological research patterns.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    """
    # First pass: calculate age group means for imputation
    age_group_means = calculate_age_group_means(input_file)
    
    rows_processed = 0
    rows_recalibrated = 0
    actual_imputed = 0
    perceived_imputed = 0
    
    # Statistics for verification
    gaps_by_age_group = defaultdict(list)
    
    rows = []
    
    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        # Process each row
        for row in reader:
            rows_processed += 1
            
            age = row.get('age', '')
            actual = row.get('actual_productivity_score', '')
            perceived = row.get('perceived_productivity_score', '')
            
            # Skip if age is missing
            if not age:
                rows.append(row)
                continue
            
            age_group = get_age_group(age)
            
            # Skip if age is out of expected range
            if age_group is None:
                rows.append(row)
                continue
            
            # Handle missing actual_productivity_score
            if not actual:
                if age_group in age_group_means:
                    actual = age_group_means[age_group]
                    row['actual_productivity_score'] = str(actual)
                    actual_imputed += 1
                else:
                    # Can't impute, skip this row
                    rows.append(row)
                    continue
            else:
                actual = float(actual)
            
            # Get gap range for age group
            gap_config = AGE_GROUP_GAPS[age_group]
            gap_min = gap_config['gap_min']
            gap_max = gap_config['gap_max']
            
            # Generate random gap within the age-appropriate range
            gap = random.uniform(gap_min, gap_max)
            
            # Calculate new perceived score
            new_perceived = actual + gap
            
            # Apply constraints: scores must be between 0-10
            new_perceived = max(0.0, min(10.0, new_perceived))
            
            # Update the row
            row['perceived_productivity_score'] = str(new_perceived)
            rows_recalibrated += 1
            
            # Track for verification
            actual_gap = new_perceived - actual
            gaps_by_age_group[age_group].append(actual_gap)
            
            rows.append(row)
    
    # Write output file
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Print summary
    print(f"Processing complete!")
    print(f"  Total rows processed: {rows_processed}")
    print(f"  Rows recalibrated: {rows_recalibrated}")
    print(f"  Actual scores imputed: {actual_imputed}")
    print(f"  Perceived scores calculated: {rows_recalibrated}")
    print(f"  Output file: {output_file}")
    
    return gaps_by_age_group


def verify_gaps(gaps_by_age_group):
    """
    Verify the productivity gaps match expected research-based patterns.
    
    Args:
        gaps_by_age_group: Dictionary mapping age group to list of gaps
    """
    print("\n" + "=" * 80)
    print("Average Productivity Gap by Age Group (Perceived - Actual):")
    print("=" * 80)
    
    for group_key in ['teen', 'young_adult', 'adult', 'middle_aged', 'senior']:
        if group_key in gaps_by_age_group:
            gaps = gaps_by_age_group[group_key]
            config = AGE_GROUP_GAPS[group_key]
            
            mean_gap = sum(gaps) / len(gaps)
            min_gap = min(gaps)
            max_gap = max(gaps)
            
            print(f"\n{config['description']}:")
            print(f"  Expected Range: [{config['gap_min']:.1f}, {config['gap_max']:.1f}]")
            print(f"  Count: {len(gaps)}")
            print(f"  Mean Gap: {mean_gap:.4f}")
            print(f"  Min Gap: {min_gap:.4f}")
            print(f"  Max Gap: {max_gap:.4f}")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    input_file = 'social_media_vs_productivity_CORRECTED.csv'
    output_file = 'social_media_vs_productivity_CORRECTED.csv'
    
    print("Recalibrating productivity scores based on psychological research...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    gaps_by_age_group = recalibrate_productivity_scores(input_file, output_file)
    verify_gaps(gaps_by_age_group)
